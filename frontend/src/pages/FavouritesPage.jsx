import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";
import { useCart } from "../state/CartContext";
import { normalizeApiArray } from "../utils/normalizeApiArray";

function restaurantName(restaurant) {
  if (restaurant?.name && String(restaurant.name).trim()) return String(restaurant.name).trim();
  if (restaurant?.restaurant_id != null) return `Restaurant ${restaurant.restaurant_id}`;
  return "Restaurant";
}

export default function FavouritesPage() {
  const { user } = useAuth();
  const { addItem } = useCart();
  const [restaurants, setRestaurants] = useState([]);
  const [favouriteItems, setFavouriteItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cartMessage, setCartMessage] = useState("");

  const isCustomerSignedIn = user?.role === "customer" && !user?.requires2FA;

  useEffect(() => {
    if (!isCustomerSignedIn) {
      setRestaurants([]);
      setFavouriteItems([]);
      setLoading(false);
      setError("");
      setCartMessage("");
      return;
    }

    let cancelled = false;
    (async () => {
      setLoading(true);
      setError("");
      try {
        const [restaurantData, favouriteData] = await Promise.all([
          api.restaurants.getAll(),
          api.customer.getFavourites(),
        ]);
        const favouriteKeys = Array.isArray(favouriteData) ? favouriteData : [];
        const favouriteItemData = await Promise.all(
          favouriteKeys.map(async (itemKey) => {
            try {
              const item = await api.items.byKey(itemKey);
              return item && typeof item === "object" ? { ...item, favouriteKey: itemKey } : null;
            } catch {
              return null;
            }
          })
        );
        if (cancelled) return;
        setRestaurants(normalizeApiArray(restaurantData));
        setFavouriteItems(favouriteItemData.filter(Boolean));
      } catch (e) {
        if (cancelled) return;
        setRestaurants([]);
        setFavouriteItems([]);
        setError(e?.message || "Could not load favourite items.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [isCustomerSignedIn]);

  const favouriteItemsByRestaurant = useMemo(() => {
    if (favouriteItems.length === 0 || restaurants.length === 0) return [];

    const byRestaurantId = new Map(
      restaurants
        .filter((restaurant) => restaurant?.restaurant_id != null)
        .map((restaurant) => [String(restaurant.restaurant_id), restaurant])
    );

    const grouped = new Map();

    favouriteItems.forEach((item) => {
      const restaurantId = item?.restaurant_id != null ? String(item.restaurant_id) : "";
      if (!restaurantId) return;

      const restaurant = byRestaurantId.get(restaurantId);
      if (!restaurant) return;

      const groupKey = String(restaurant.restaurant_id);
      if (!grouped.has(groupKey)) {
        grouped.set(groupKey, {
          restaurant,
          items: [],
        });
      }

      grouped.get(groupKey).items.push(item);
    });

    return Array.from(grouped.values())
      .filter((entry) => entry.items.length > 0)
      .sort((a, b) => restaurantName(a.restaurant).localeCompare(restaurantName(b.restaurant)))
      .map((entry) => ({
        ...entry,
        items: entry.items.sort((a, b) =>
          String(a?.item_name ?? "Menu item").localeCompare(String(b?.item_name ?? "Menu item"))
        ),
      }));
  }, [favouriteItems, restaurants]);

  return (
    <section className="card favourites-page">
      <header className="page-header-block">
        <h1 className="page-title">Favourites</h1>
        <p className="page-lede muted">
          See every favourite item you&apos;ve saved, grouped by the restaurants that have one.
        </p>
      </header>

      <section className="panel favourites-section" aria-labelledby="favourite-items-heading">
        <div className="restaurant-favourites__header">
          <h2 id="favourite-items-heading" className="restaurant-menu-section__title">
            Favourite items
          </h2>
          {!isCustomerSignedIn && (
            <p className="muted small-print">Sign in as a customer to view your saved items.</p>
          )}
        </div>

        {loading && <p className="muted">Loading favourite items…</p>}
        {!loading && error && <p className="error">{error}</p>}
        {!loading && !error && isCustomerSignedIn && favouriteItemsByRestaurant.length === 0 && (
          <p className="muted">You have no favourite items yet.</p>
        )}

        {!loading && !error && isCustomerSignedIn && favouriteItemsByRestaurant.length > 0 && (
          <div className="favourites-restaurant-list">
            {favouriteItemsByRestaurant.map(({ restaurant, items }) => (
              <article className="panel favourites-restaurant-card" key={restaurant.restaurant_id}>
                <div className="favourites-restaurant-card__header">
                  <div>
                    <h3 className="favourites-restaurant-card__title">{restaurantName(restaurant)}</h3>
                    <p className="muted small-print">
                      {items.length} favourite item{items.length === 1 ? "" : "s"}
                    </p>
                  </div>
                  <Link
                    className="restaurant-browse-card__cta"
                    to={`/restaurants/${restaurant.restaurant_id}`}
                    state={{ restaurant }}
                  >
                    View menu
                  </Link>
                </div>

                <div className="restaurant-favourites__list">
                  {items.map((item) => (
                    <div className="restaurant-favourites__card" key={item.favouriteKey}>
                      <div>
                        <h4 className="menu-item-card__name">
                          {item?.item_name && String(item.item_name).trim() ? String(item.item_name).trim() : "Menu item"}
                        </h4>
                        <p className="menu-item-card__price">
                          ${Number.isFinite(Number(item?.cost ?? item?.price))
                            ? Number(item.cost ?? item.price).toFixed(2)
                            : "0.00"}
                        </p>
                        <p className="muted small-print">Saved from {restaurantName(restaurant)}</p>
                      </div>
                      <button
                        type="button"
                        className="menu-item-card__add"
                        onClick={() => {
                          const result = addItem(item);
                          if (!result?.ok) setCartMessage(result?.message || "Unable to add item to cart.");
                          else setCartMessage("");
                        }}
                      >
                        Add to cart
                      </button>
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {cartMessage && (
        <p className="error" role="status">
          {cartMessage}
        </p>
      )}
    </section>
  );
}
