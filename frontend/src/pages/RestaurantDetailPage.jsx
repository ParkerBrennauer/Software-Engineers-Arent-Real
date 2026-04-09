import React, { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useCart } from "../state/CartContext";
import { useAuth } from "../state/AuthContext";
import { useRestaurantWorkspace } from "../state/RestaurantWorkspaceContext";
import CartPanel from "../components/CartPanel";
import { normalizeApiArray } from "../utils/normalizeApiArray";
import { dietaryTags } from "../utils/formatItemDietary";

const DIETARY_FIELDS = [
  ["vegan", "Vegan"],
  ["vegetarian", "Vegetarian"],
  ["gluten_free", "Gluten free"],
  ["dairy_free", "Dairy free"],
  ["nut_free", "Nut free"],
  ["halal", "Halal"],
  ["kosher", "Kosher"],
];

function normalizeDietaryInput(dietary) {
  const source = dietary && typeof dietary === "object" ? dietary : {};
  return {
    vegan: Boolean(source.vegan),
    vegetarian: Boolean(source.vegetarian),
    gluten_free: Boolean(source.gluten_free),
    dairy_free: Boolean(source.dairy_free),
    nut_free: Boolean(source.nut_free),
    halal: Boolean(source.halal),
    kosher: Boolean(source.kosher),
  };
}

function createItemFormState(item, restaurantId, fallbackCuisine = "") {
  const dietary = normalizeDietaryInput(item?.dietary);
  return {
    item_name: item?.item_name != null ? String(item.item_name) : "",
    restaurant_id: restaurantId,
    cost: item?.cost != null ? String(item.cost) : "",
    cuisine: item?.cuisine != null && String(item.cuisine).trim() ? String(item.cuisine) : fallbackCuisine,
    dietary,
  };
}

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
  const { linkedRestaurant, status: workspaceStatus, beginSwitchRestaurant } = useRestaurantWorkspace();

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
  const [editingItemKey, setEditingItemKey] = useState("");
  const [editForm, setEditForm] = useState(() => createItemFormState(null, idValid ? idNum : 0));
  const [editBusy, setEditBusy] = useState(false);
  const [editError, setEditError] = useState("");
  const [editMessage, setEditMessage] = useState("");
  const [createForm, setCreateForm] = useState(() => createItemFormState(null, idValid ? idNum : 0));
  const [createBusy, setCreateBusy] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createMessage, setCreateMessage] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);

  const isCustomerSignedIn = user?.role === "customer" && !user?.requires2FA;
  const ownerCanManageItems =
    user?.role === "owner" &&
    !user?.requires2FA &&
    workspaceStatus === "ready" &&
    Number(linkedRestaurant?.id) === idNum;

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

  useEffect(() => {
    setCreateForm((prev) => ({
      ...prev,
      restaurant_id: idNum,
      cuisine:
        prev.cuisine && String(prev.cuisine).trim()
          ? prev.cuisine
          : restaurant?.cuisine != null && String(restaurant.cuisine).trim()
            ? String(restaurant.cuisine)
            : "",
    }));
  }, [idNum, restaurant?.cuisine]);

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

  function setDietaryField(target, name, checked) {
    if (target === "edit") {
      setEditForm((prev) => ({
        ...prev,
        dietary: {
          ...prev.dietary,
          [name]: checked,
        },
      }));
      return;
    }
    setCreateForm((prev) => ({
      ...prev,
      dietary: {
        ...prev.dietary,
        [name]: checked,
      },
    }));
  }

  function startEditingItem(item) {
    const itemKey = `${String(item?.item_name ?? "Menu item").trim()}_${item?.restaurant_id ?? idNum}`;
    setEditingItemKey(itemKey);
    setEditForm(createItemFormState(item, item?.restaurant_id ?? idNum, restaurant?.cuisine ?? ""));
    setEditError("");
    setEditMessage("");
  }

  function resetCreateForm() {
    setCreateForm(createItemFormState(null, idNum, restaurant?.cuisine ?? ""));
  }

  async function handleItemUpdate(item) {
    const currentItemKey = `${String(item?.item_name ?? "Menu item").trim()}_${item?.restaurant_id ?? idNum}`;
    const nextName = String(editForm.item_name || "").trim();
    const nextCuisine = String(editForm.cuisine || "").trim();
    const nextCost = Number(editForm.cost);

    setEditError("");
    setEditMessage("");

    if (!nextName) {
      setEditError("Item name is required.");
      return;
    }
    if (!nextCuisine) {
      setEditError("Cuisine is required.");
      return;
    }
    if (!Number.isFinite(nextCost) || nextCost < 0) {
      setEditError("Cost must be 0 or higher.");
      return;
    }

    setEditBusy(true);
    try {
      const updated = await api.items.update(currentItemKey, {
        item_name: nextName,
        cost: nextCost,
        cuisine: nextCuisine,
        dietary: normalizeDietaryInput(editForm.dietary),
      });
      const normalized = {
        ...item,
        ...updated,
        restaurant_id: updated?.restaurant_id ?? item?.restaurant_id ?? idNum,
        dietary: normalizeDietaryInput(updated?.dietary ?? editForm.dietary),
      };
      setMenuItems((prev) =>
        prev.map((row) => {
          const rowKey = `${String(row?.item_name ?? "Menu item").trim()}_${row?.restaurant_id ?? idNum}`;
          return rowKey === currentItemKey ? normalized : row;
        })
      );
      setEditMessage("Item updated.");
      setEditingItemKey("");
    } catch (e) {
      setEditError(e?.message || "Could not update item.");
    } finally {
      setEditBusy(false);
    }
  }

  async function handleCreateItem(e) {
    e.preventDefault();
    const nextName = String(createForm.item_name || "").trim();
    const nextCuisine = String(createForm.cuisine || "").trim();
    const nextCost = Number(createForm.cost);

    setCreateError("");
    setCreateMessage("");

    if (!nextName) {
      setCreateError("Item name is required.");
      return;
    }
    if (!nextCuisine) {
      setCreateError("Cuisine is required.");
      return;
    }
    if (!Number.isFinite(nextCost) || nextCost < 0) {
      setCreateError("Cost must be 0 or higher.");
      return;
    }

    setCreateBusy(true);
    try {
      const created = await api.items.create({
        item_name: nextName,
        restaurant_id: idNum,
        cost: nextCost,
        cuisine: nextCuisine,
        times_ordered: 0,
        avg_rating: 0,
        dietary: normalizeDietaryInput(createForm.dietary),
      });
      setMenuItems((prev) => [
        ...prev,
        {
          ...created,
          restaurant_id: created?.restaurant_id ?? idNum,
          dietary: normalizeDietaryInput(created?.dietary ?? createForm.dietary),
        },
      ]);
      setCreateMessage("Item created.");
      setShowCreateForm(false);
      resetCreateForm();
    } catch (e) {
      setCreateError(e?.message || "Could not create item.");
    } finally {
      setCreateBusy(false);
    }
  }

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
        <div className="restaurant-menu-section__header">
          <h2 id="restaurant-menu-heading" className="restaurant-menu-section__title">
            Menu
          </h2>
          {ownerCanManageItems && (
            <div className="restaurant-menu-section__actions">
              <button
                type="button"
                className="menu-item-card__edit"
                onClick={() => {
                  setShowCreateForm((prev) => !prev);
                  setCreateError("");
                  setCreateMessage("");
                }}
              >
                {showCreateForm ? "Close new item" : "Create item"}
              </button>
              <button type="button" className="owner-venue-bar__linkish" onClick={beginSwitchRestaurant}>
                Switch venue
              </button>
            </div>
          )}
        </div>
        {user?.role === "owner" && workspaceStatus === "ready" && Number(linkedRestaurant?.id) !== idNum && (
          <p className="muted small-print">
            Item editing is only available on your linked restaurant. Switch to your venue to manage menu items here.
          </p>
        )}
        {ownerCanManageItems && showCreateForm && (
          <form className="panel owner-item-form" onSubmit={handleCreateItem}>
            <h3 className="owner-item-form__title">Create a menu item</h3>
            <div className="row form-grid">
              <label className="field">
                <span>Name</span>
                <input
                  value={createForm.item_name}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, item_name: e.target.value }))}
                  placeholder="Item name"
                  disabled={createBusy}
                  required
                />
              </label>
              <label className="field">
                <span>Cost</span>
                <input
                  inputMode="decimal"
                  value={createForm.cost}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, cost: e.target.value }))}
                  placeholder="0.00"
                  disabled={createBusy}
                  required
                />
              </label>
              <label className="field">
                <span>Cuisine</span>
                <input
                  value={createForm.cuisine}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, cuisine: e.target.value }))}
                  placeholder="Cuisine"
                  disabled={createBusy}
                  required
                />
              </label>
            </div>
            <fieldset className="owner-item-form__dietary">
              <legend>Dietary tags</legend>
              <div className="owner-item-form__dietary-grid">
                {DIETARY_FIELDS.map(([name, label]) => (
                  <label className="checkbox-inline" key={`create_${name}`}>
                    <input
                      type="checkbox"
                      checked={Boolean(createForm.dietary?.[name])}
                      onChange={(e) => setDietaryField("create", name, e.target.checked)}
                      disabled={createBusy}
                    />
                    {label}
                  </label>
                ))}
              </div>
            </fieldset>
            <div className="owner-item-form__actions">
              <button type="submit" disabled={createBusy}>
                {createBusy ? "Creating…" : "Save item"}
              </button>
              <button
                type="button"
                className="button-link"
                onClick={() => {
                  setShowCreateForm(false);
                  setCreateError("");
                  setCreateMessage("");
                  resetCreateForm();
                }}
                disabled={createBusy}
              >
                Cancel
              </button>
            </div>
            {createError && <p className="error">{createError}</p>}
            {createMessage && <p className="success">{createMessage}</p>}
          </form>
        )}
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
                  {isCustomerSignedIn && (
                    <button
                      type="button"
                      className={`menu-item-card__favourite${isFavourite ? " menu-item-card__favourite--active" : ""}`}
                      aria-pressed={isFavourite}
                      onClick={() => handleFavouriteToggle(item)}
                      disabled={favouriteBusy}
                    >
                      {favouriteBusy ? "Saving…" : isFavourite ? "★ Favourite" : "☆ Favourite"}
                    </button>
                  )}
                </div>
                <p className="menu-item-card__price">${safePrice.toFixed(2)}</p>
                {item?.cuisine != null && String(item.cuisine).trim() && (
                  <p className="muted small-print">{item.cuisine}</p>
                )}
                {extra && <p className="small-print menu-item-card__extra">{extra}</p>}
                {ownerCanManageItems && (
                  <button
                    type="button"
                    className="menu-item-card__edit"
                    onClick={() => startEditingItem(item)}
                    disabled={editBusy && editingItemKey === itemKey}
                  >
                    Edit item
                  </button>
                )}
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
                {ownerCanManageItems && editingItemKey === itemKey && (
                  <form
                    className="owner-item-form owner-item-form--inline"
                    onSubmit={(e) => {
                      e.preventDefault();
                      handleItemUpdate(item);
                    }}
                  >
                    <div className="row form-grid">
                      <label className="field">
                        <span>Name</span>
                        <input
                          value={editForm.item_name}
                          onChange={(e) => setEditForm((prev) => ({ ...prev, item_name: e.target.value }))}
                          disabled={editBusy}
                          required
                        />
                      </label>
                      <label className="field">
                        <span>Cost</span>
                        <input
                          inputMode="decimal"
                          value={editForm.cost}
                          onChange={(e) => setEditForm((prev) => ({ ...prev, cost: e.target.value }))}
                          disabled={editBusy}
                          required
                        />
                      </label>
                      <label className="field">
                        <span>Cuisine</span>
                        <input
                          value={editForm.cuisine}
                          onChange={(e) => setEditForm((prev) => ({ ...prev, cuisine: e.target.value }))}
                          disabled={editBusy}
                          required
                        />
                      </label>
                    </div>
                    <fieldset className="owner-item-form__dietary">
                      <legend>Dietary tags</legend>
                      <div className="owner-item-form__dietary-grid">
                        {DIETARY_FIELDS.map(([name, label]) => (
                          <label className="checkbox-inline" key={`edit_${itemKey}_${name}`}>
                            <input
                              type="checkbox"
                              checked={Boolean(editForm.dietary?.[name])}
                              onChange={(e) => setDietaryField("edit", name, e.target.checked)}
                              disabled={editBusy}
                            />
                            {label}
                          </label>
                        ))}
                      </div>
                    </fieldset>
                    <div className="owner-item-form__actions">
                      <button type="submit" disabled={editBusy}>
                        {editBusy ? "Saving…" : "Save changes"}
                      </button>
                      <button
                        type="button"
                        className="button-link"
                        onClick={() => {
                          setEditingItemKey("");
                          setEditError("");
                          setEditMessage("");
                          setEditForm(createItemFormState(null, idNum, restaurant?.cuisine ?? ""));
                        }}
                        disabled={editBusy}
                      >
                        Cancel
                      </button>
                    </div>
                    {editError && <p className="error">{editError}</p>}
                    {editMessage && <p className="success">{editMessage}</p>}
                  </form>
                )}
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
