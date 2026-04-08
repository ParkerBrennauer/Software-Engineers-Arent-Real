import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useCart } from "../state/CartContext";
import CartPanel from "../components/CartPanel";

export default function RestaurantsPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [selectedRestaurantId, setSelectedRestaurantId] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [menuLoading, setMenuLoading] = useState(false);
  const [error, setError] = useState("");
  const { addItem, items } = useCart();

  function normalizeList(data) {
    if (Array.isArray(data)) return data;
    if (data && typeof data === "object") return Object.values(data);
    return [];
  }

  async function loadAll() {
    setLoading(true);
    setError("");
    try {
      setRestaurants(normalizeList(await api.restaurants.getAll()));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    async function init() {
      setLoading(true);
      setError("");
      try {
        const data = await api.restaurants.getAll();
        if (active) setRestaurants(normalizeList(data));
      } catch (err) {
        if (active) setError(err.message);
      } finally {
        if (active) setLoading(false);
      }
    }
    init();
    return () => {
      active = false;
    };
  }, []);

  async function runSearch() {
    setLoading(true);
    setError("");
    try {
      if (!query.trim()) {
        await loadAll();
        return;
      }
      setRestaurants(normalizeList(await api.restaurants.search(query)));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const cards = useMemo(
    () =>
      restaurants.map((r) => (
        <article className="panel" key={r.restaurant_id || JSON.stringify(r)}>
          <h3>Restaurant {r.restaurant_id ?? "Unknown"}</h3>
          <p>Cuisine: {r.cuisine || "n/a"}</p>
          <p>Rating: {r.avg_ratings ?? "n/a"}</p>
          <button
            onClick={async () => {
              setError("");
              setSelectedRestaurantId(r.restaurant_id);
              setMenuLoading(true);
              try {
                const menu = await api.restaurants.menu(r.restaurant_id);
                setMenuItems(normalizeList(menu));
              } catch {
                try {
                  const fallback = await api.items.byRestaurant(r.restaurant_id);
                  setMenuItems(normalizeList(fallback));
                } catch (err) {
                  setMenuItems([]);
                  setError(err.message);
                } finally {
                  setMenuLoading(false);
                }
                return;
              }
              setMenuLoading(false);
            }}
          >
            View menu
          </button>
        </article>
      )),
    [restaurants]
  );

  return (
    <section className="card">
      <h2>Restaurant discovery</h2>
      {items.length > 0 && (
        <div className="promo-banner" role="status">
          <span className="promo-badge">Promo</span>
          <span>
            Have a code? Apply it in your cart on the <Link to="/orders">Orders</Link> page before checkout.
          </span>
        </div>
      )}
      <div className="row">
        <input placeholder="Search by id (backend limitation)" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button onClick={runSearch}>Search</button>
        <button onClick={loadAll}>Refresh</button>
      </div>
      {loading && <p>Loading restaurants...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && cards.length === 0 && <p className="muted">No restaurants returned.</p>}
      <div className="grid cards">{cards}</div>
      <section className="card">
        <h3>Menu {selectedRestaurantId ? `for Restaurant ${selectedRestaurantId}` : ""}</h3>
        {menuLoading && <p>Loading menu...</p>}
        {!menuLoading && menuItems.length === 0 && <p className="muted">Select a restaurant to load menu items.</p>}
        <div className="grid cards">
          {menuItems.map((item) => (
            <article className="panel" key={`${item.item_name}_${item.restaurant_id}`}>
              <h4>{item.item_name}</h4>
              <p>${Number(item.cost ?? 0).toFixed(2)}</p>
              <p className="muted">{item.cuisine}</p>
              <button
                onClick={() => {
                  const result = addItem(item);
                  if (!result?.ok) setError(result.message || "Unable to add item to cart.");
                }}
              >
                Add to cart
              </button>
            </article>
          ))}
        </div>
      </section>
      <CartPanel />
    </section>
  );
}

