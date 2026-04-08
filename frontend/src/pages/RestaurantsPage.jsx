import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { useCart } from "../state/CartContext";
import CartPanel from "../components/CartPanel";

export default function RestaurantsPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [selectedRestaurantId, setSelectedRestaurantId] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { addItem } = useCart();

  async function loadAll() {
    setLoading(true);
    setError("");
    try {
      setRestaurants(await api.restaurants.getAll());
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
        if (active) setRestaurants(Array.isArray(data) ? data : []);
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
      setRestaurants(await api.restaurants.search(query));
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
              try {
                const menu = await api.restaurants.menu(r.restaurant_id);
                setMenuItems(Array.isArray(menu) ? menu : []);
              } catch {
                try {
                  const fallback = await api.items.byRestaurant(r.restaurant_id);
                  setMenuItems(Array.isArray(fallback) ? fallback : []);
                } catch (err) {
                  setMenuItems([]);
                  setError(err.message);
                }
              }
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
        {menuItems.length === 0 && <p className="muted">Select a restaurant to load menu items.</p>}
        <div className="grid cards">
          {menuItems.map((item) => (
            <article className="panel" key={`${item.item_name}_${item.restaurant_id}`}>
              <h4>{item.item_name}</h4>
              <p>${Number(item.cost ?? 0).toFixed(2)}</p>
              <p className="muted">{item.cuisine}</p>
              <button onClick={() => addItem(item)}>Add to cart</button>
            </article>
          ))}
        </div>
      </section>
      <CartPanel />
    </section>
  );
}

