import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { normalizeApiArray } from "../utils/normalizeApiArray";

export default function RestaurantsPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadAll() {
    setLoading(true);
    setError("");
    try {
      setRestaurants(normalizeApiArray(await api.restaurants.getAll()));
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
        if (active) setRestaurants(normalizeApiArray(data));
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
      setRestaurants(normalizeApiArray(await api.restaurants.search(query)));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const cards = useMemo(
    () =>
      restaurants
        .filter((r) => r?.restaurant_id != null)
        .map((r) => {
          const id = r.restaurant_id;
          const safeId = String(id);
          return (
            <Link
              key={safeId}
              className="restaurant-browse-card panel"
              to={`/restaurants/${safeId}`}
              state={{ restaurant: r }}
            >
              <h3>Restaurant {id}</h3>
              <p>Cuisine: {r.cuisine || "—"}</p>
              <p>Rating: {r.avg_ratings != null && r.avg_ratings !== "" ? Number(r.avg_ratings).toFixed(1) : "—"}</p>
              <span className="restaurant-browse-card__cta">View menu</span>
            </Link>
          );
        }),
    [restaurants]
  );

  return (
    <section className="card restaurants-browse">
      <header className="page-header-block">
        <h1 className="page-title">Restaurants</h1>
        <p className="page-lede muted">
          Tap a restaurant to see the full menu. Your cart stays in the header while you browse.
        </p>
      </header>
      <div className="row">
        <input placeholder="Search restaurants" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button type="button" onClick={runSearch}>
          Search
        </button>
        <button type="button" onClick={loadAll}>
          Refresh
        </button>
      </div>
      {loading && <p>Loading restaurants...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && cards.length === 0 && <p className="muted">No restaurants returned.</p>}
      <div className="grid cards">{cards}</div>
    </section>
  );
}
