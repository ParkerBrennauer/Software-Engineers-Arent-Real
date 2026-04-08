import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";

export default function RestaurantsPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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
    loadAll();
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
    </section>
  );
}

