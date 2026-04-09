import React, { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useCart } from "../state/CartContext";
import { useAuth } from "../state/AuthContext";
import CartPanel from "../components/CartPanel";
import { normalizeApiArray } from "../utils/normalizeApiArray";
import { dietaryTags } from "../utils/formatItemDietary";

function formatLocation(loc) {
  if (loc == null) return null;
  if (Array.isArray(loc) && loc.length >= 2) {
    const [a, b] = loc;
    if (typeof a === "number" && typeof b === "number") {
      return `${a.toFixed(4)}, ${b.toFixed(4)}`;
    }
    return String(loc);
  }
  if (typeof loc === "string" && loc.trim()) return loc.trim();
  return null;
}

export default function RestaurantDetailPage() {
  const { restaurantId: idParam } = useParams();
  const location = useLocation();
  const { addItem } = useCart();
  const { user } = useAuth();

  const idNum = Number(idParam);
  const idValid = Number.isInteger(idNum) && idNum > 0;

  const [restaurant, setRestaurant] = useState(null);
  const [metaError, setMetaError] = useState("");
  const [menuItems, setMenuItems] = useState([]);
  const [menuLoading, setMenuLoading] = useState(false);
  const [menuError, setMenuError] = useState("");
  const [cartMessage, setCartMessage] = useState("");
  const [favouriteKeys, setFavouriteKeys] = useState([]);
  const [favouriteLoading, setFavouriteLoading] = useState(false);
  const [favouriteError, setFavouriteError] = useState("");
  const [favouriteActionKey, setFavouriteActionKey] = useState("");

  const isCustomerSignedIn = user?.role === "customer" && !user?.requires2FA;

  const displayName = useMemo(() => {
    if (restaurant?.name && String(restaurant.name).trim()) return String(restaurant.name).trim();
    return `Restaurant ${idValid ? idNum : idParam ?? "—"}`;
  }, [restaurant, idValid, idNum, idParam]);

  const favouriteItems = useMemo(() => {
    if (menuItems.length === 0 || favouriteKeys.length === 0) return [];
    const menuByKey = new Map(
      menuItems.map((item) => [`${String(item?.item_name ?? "Menu item").trim()}_${item?.restaurant_id ?? idNum}`, item])
    );
    return favouriteKeys.map((key) => menuByKey.get(key)).filter(Boolean);
  }, [favouriteKeys, menuItems, idNum]);

  const stateRestaurantId = location.state?.restaurant?.restaurant_id;

  useEffect(() => {
    if (!idValid) return;
    const fromNav = location.state?.restaurant;
    if (fromNav && Number(fromNav.restaurant_id) === idNum) {
      setMetaError("");
      setRestaurant(fromNav);
      return;
    }
    let cancelled = false;
    (async () => {
      setMetaError("");
      try {
        const data = await api.restaurants.getAll();
        const list = normalizeApiArray(data);
        const found = list.find((r) => Number(r?.restaurant_id) === idNum) || null;
        if (!cancelled) setRestaurant(found);
      } catch (e) {
        if (!cancelled) setMetaError(e?.message || "Could not load restaurant details.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [idValid, idNum, stateRestaurantId, location.pathname]);

  useEffect(() => {
    if (!idValid) return;
    let cancelled = false;
    (async () => {
      setMenuLoading(true);
      setMenuError("");
      try {
        const menu = await api.restaurants.menu(idNum);
        if (!cancelled) setMenuItems(normalizeApiArray(menu));
      } catch {
        try {
          const fallback = await api.items.byRestaurant(idNum);
          if (!cancelled) setMenuItems(normalizeApiArray(fallback));
        } catch (e) {
          if (!cancelled) {
            setMenuItems([]);
            setMenuError(e?.message || "Could not load menu.");
          }
        }
      } finally {
        if (!cancelled) setMenuLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [idValid, idNum]);

  useEffect(() => {
    if (!idValid || !isCustomerSignedIn) {
      setFavouriteKeys([]);
      setFavouriteError("");
      setFavouriteLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setFavouriteLoading(true);
      setFavouriteError("");
      try {
        const favourites = await api.customer.getFavourites();
        if (!cancelled) {
          setFavouriteKeys(Array.isArray(favourites) ? favourites : []);
        }
      } catch (e) {
        if (!cancelled) {
          setFavouriteKeys([]);
          setFavouriteError(e?.message || "Could not load favourite items.");
        }
      } finally {
        if (!cancelled) setFavouriteLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [idValid, isCustomerSignedIn]);

  async function handleFavouriteToggle(item) {
    const itemKey = `${String(item?.item_name ?? "Menu item").trim()}_${item?.restaurant_id ?? idNum}`;
    setFavouriteActionKey(itemKey);
    setFavouriteError("");
    try {
      const result = await api.customer.toggleFavouriteItem(itemKey);
      setFavouriteKeys((prev) => {
        const current = Array.isArray(prev) ? prev : [];
        const withoutCurrentRestaurant = current.filter((key) => !key.endsWith(`_${item?.restaurant_id ?? idNum}`));
        if (result === "removed") {
          return withoutCurrentRestaurant.filter((key) => key !== itemKey);
        }
        return [...withoutCurrentRestaurant, itemKey];
      });
    } catch (e) {
      setFavouriteError(e?.message || "Could not update favourite item.");
    } finally {
      setFavouriteActionKey("");
    }
  }

  if (!idValid) {
    return (
      <section className="card restaurant-storefront">
        <div className="panel access-restricted-notice" role="alert">
          <p>That restaurant link is not valid.</p>
          <Link className="button-link" to="/restaurants">
            Back to restaurants
          </Link>
        </div>
      </section>
    );
  }

  const cuisine = restaurant?.cuisine != null && String(restaurant.cuisine).trim() ? restaurant.cuisine : null;
  const rating =
    restaurant?.avg_ratings != null && restaurant.avg_ratings !== ""
      ? Number(restaurant.avg_ratings)
      : null;
  const ratingLabel = rating != null && Number.isFinite(rating) ? rating.toFixed(1) : null;
  const locLabel = formatLocation(restaurant?.location);
  const description =
    restaurant?.description != null && String(restaurant.description).trim()
      ? String(restaurant.description).trim()
      : null;

  return (
    <section className="card restaurant-storefront">
      <nav className="restaurant-breadcrumb muted small-print" aria-label="Breadcrumb">
        <Link to="/restaurants">Restaurants</Link>
        <span aria-hidden="true"> / </span>
        <span>{displayName}</span>
      </nav>

      <header className="panel restaurant-hero">
        <h1 className="restaurant-hero__title">{displayName}</h1>
        <div className="restaurant-hero__meta">
          {cuisine && (
            <p>
              <span className="restaurant-hero__label">Cuisine</span> {cuisine}
            </p>
          )}
          {ratingLabel && (
            <p>
              <span className="restaurant-hero__label">Rating</span> {ratingLabel} / 5
            </p>
          )}
          {locLabel ? (
            <p>
              <span className="restaurant-hero__label">Location</span> {locLabel}
            </p>
          ) : (
            <p className="muted">
              <span className="restaurant-hero__label">Location</span> Not available
            </p>
          )}
        </div>
        {description && <p className="restaurant-hero__desc">{description}</p>}
        {!cuisine && !ratingLabel && !description && !locLabel && (
          <p className="muted small-print">Limited profile data is available for this listing.</p>
        )}
        {metaError && <p className="error small-print">{metaError}</p>}
        <p className="muted small-print restaurant-hero__promo">
          Promo codes can be added in your cart on the <Link to="/orders">Orders</Link> page at checkout.
        </p>
      </header>

      <section className="panel restaurant-favourites" aria-labelledby="restaurant-favourites-heading">
        <div className="restaurant-favourites__header">
          <h2 id="restaurant-favourites-heading" className="restaurant-menu-section__title">
            Favourite
          </h2>
          {!isCustomerSignedIn && (
            <p className="muted small-print">Sign in as a customer to save a favourite item here.</p>
          )}
        </div>
        {isCustomerSignedIn && favouriteLoading && <p className="muted">Loading favourite item…</p>}
        {isCustomerSignedIn && !favouriteLoading && favouriteError && <p className="error">{favouriteError}</p>}
        {isCustomerSignedIn && !favouriteLoading && !favouriteError && favouriteItems.length === 0 && (
          <p className="muted">No favourite item saved for this restaurant yet.</p>
        )}
        {isCustomerSignedIn && favouriteItems.length > 0 && (
          <div className="restaurant-favourites__list">
            {favouriteItems.map((item, idx) => {
              const name =
                item?.item_name != null && String(item.item_name).trim()
                  ? String(item.item_name).trim()
                  : "Menu item";
              const price = Number(item?.cost ?? item?.price ?? 0);
              const safePrice = Number.isFinite(price) ? price : 0;
              return (
                <article className="restaurant-favourites__card" key={`favourite_${name}_${idx}`}>
                  <div>
                    <h3 className="menu-item-card__name">{name}</h3>
                    <p className="menu-item-card__price">${safePrice.toFixed(2)}</p>
                  </div>
                  <button
                    type="button"
                    className="menu-item-card__favourite menu-item-card__favourite--active"
                    onClick={() => handleFavouriteToggle(item)}
                    disabled={favouriteActionKey === `${name}_${item?.restaurant_id ?? idNum}`}
                  >
                    {favouriteActionKey === `${name}_${item?.restaurant_id ?? idNum}` ? "Saving…" : "Remove favourite"}
                  </button>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="restaurant-menu-section" aria-labelledby="restaurant-menu-heading">
        <h2 id="restaurant-menu-heading" className="restaurant-menu-section__title">
          Menu
        </h2>
        {menuLoading && <p className="muted">Loading menu…</p>}
        {!menuLoading && menuError && <p className="error">{menuError}</p>}
        {!menuLoading && !menuError && menuItems.length === 0 && (
          <p className="muted">No menu items are available right now.</p>
        )}
        <div className="grid cards restaurant-menu-grid">
          {menuItems.map((item, idx) => {
            const keyBase =
              item?.item_name != null && String(item.item_name).trim()
                ? String(item.item_name).trim()
                : "Menu item";
            const rid = item?.restaurant_id ?? idNum;
            const tags = dietaryTags(item?.dietary);
            const price = Number(item?.cost ?? item?.price ?? 0);
            const safePrice = Number.isFinite(price) ? price : 0;
            const itemKey = `${keyBase}_${rid}`;
            const extra =
              item?.description != null && String(item.description).trim()
                ? String(item.description).trim()
                : null;
            const isFavourite = favouriteKeys.includes(itemKey);
            const favouriteBusy = favouriteActionKey === itemKey;

            return (
              <article className="panel menu-item-card" key={`${keyBase}_${rid}_${idx}`}>
                <div className="menu-item-card__top">
                  <h3 className="menu-item-card__name">{keyBase}</h3>
                  <button
                    type="button"
                    className={`menu-item-card__favourite${isFavourite ? " menu-item-card__favourite--active" : ""}`}
                    aria-pressed={isFavourite}
                    onClick={() => handleFavouriteToggle(item)}
                    disabled={!isCustomerSignedIn || favouriteBusy}
                    title={isCustomerSignedIn ? undefined : "Sign in as a customer to favourite items"}
                  >
                    {favouriteBusy ? "Saving…" : isFavourite ? "★ Favourite" : "☆ Favourite"}
                  </button>
                </div>
                <p className="menu-item-card__price">${safePrice.toFixed(2)}</p>
                {item?.cuisine != null && String(item.cuisine).trim() && (
                  <p className="muted small-print">{item.cuisine}</p>
                )}
                {extra && <p className="small-print menu-item-card__extra">{extra}</p>}
                {tags.length > 0 && (
                  <ul className="menu-item-card__tags" aria-label="Dietary information">
                    {tags.map((t) => (
                      <li key={t}>{t}</li>
                    ))}
                  </ul>
                )}
                <button
                  type="button"
                  className="menu-item-card__add"
                  onClick={() => {
                    const result = addItem(item);
                    if (!result?.ok) setCartMessage(result?.message || "Unable to add item to cart.");
                    else {
                      setCartMessage("");
                    }
                  }}
                >
                  Add to cart
                </button>
              </article>
            );
          })}
        </div>
      </section>

      {cartMessage && (
        <p className="error" role="status">
          {cartMessage}
        </p>
      )}

      <aside className="restaurant-cart-aside">
        <CartPanel />
      </aside>
    </section>
  );
}
