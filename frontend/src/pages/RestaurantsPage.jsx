import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { normalizeApiArray } from "../utils/normalizeApiArray";

const SORT_OPTIONS = [
  { value: "", label: "Default order" },
  { value: "AlphabetAsc", label: "Restaurant ID: Low to high" },
  { value: "AlphabetDesc", label: "Restaurant ID: High to low" },
  { value: "RatingAsc", label: "Rating: Low to high" },
  { value: "RatingDesc", label: "Rating: High to low" },
];

export default function RestaurantsPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [sort, setSort] = useState("");
  const [filterOptions, setFilterOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function captureFilterOptions(rows) {
    const nextOptions = [...new Set(normalizeApiArray(rows).map((r) => r?.cuisine).filter(Boolean))].sort((a, b) =>
      a.localeCompare(b)
    );
    setFilterOptions((current) =>
      (current.length ? [...new Set([...current, ...nextOptions])] : nextOptions).sort((a, b) => a.localeCompare(b))
    );
  }

  async function loadAll() {
    setLoading(true);
    setError("");
    try {
      const data = normalizeApiArray(await api.restaurants.getAll());
      captureFilterOptions(data);
      setRestaurants(data);
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
        const data = normalizeApiArray(await api.restaurants.getAll());
        if (active) {
          captureFilterOptions(data);
          setRestaurants(data);
        }
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
      const trimmedQuery = query.trim();
      const hasAdvancedControls = selectedFilters.length > 0 || Boolean(sort);

      if (!trimmedQuery && !hasAdvancedControls) {
        await loadAll();
        return;
      }

      if (!hasAdvancedControls) {
        setRestaurants(normalizeApiArray(await api.restaurants.search(trimmedQuery)));
        return;
      }

      const filtersForRequest = selectedFilters.length > 0 ? selectedFilters : filterOptions;
      const advancedResults = await api.restaurants.advancedSearch({
        query: trimmedQuery,
        filters: filtersForRequest,
        sort,
      });
      setRestaurants(normalizeApiArray(advancedResults));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function toggleFilter(nextFilter) {
    setSelectedFilters((current) =>
      current.includes(nextFilter) ? current.filter((filter) => filter !== nextFilter) : [...current, nextFilter]
    );
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
      <div className="row restaurants-browse__toolbar">
        <input
          placeholder="Search restaurants"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Search restaurants"
        />
        <details className="restaurants-browse__dropdown">
          <summary>Filters {selectedFilters.length > 0 ? `(${selectedFilters.length})` : ""}</summary>
          <div className="restaurants-browse__dropdown-panel">
            {filterOptions.length === 0 ? (
              <p className="muted restaurants-browse__dropdown-empty">No cuisine filters available yet.</p>
            ) : (
              filterOptions.map((filter) => (
                <label key={filter} className="checkbox-inline restaurants-browse__checkbox">
                  <input
                    type="checkbox"
                    checked={selectedFilters.includes(filter)}
                    onChange={() => toggleFilter(filter)}
                  />
                  <span>{filter}</span>
                </label>
              ))
            )}
          </div>
        </details>
        <select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort restaurants">
          {SORT_OPTIONS.map((option) => (
            <option key={option.value || "default"} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <button type="button" onClick={runSearch}>
          Search
        </button>
        <button type="button" onClick={loadAll}>
          Refresh
        </button>
      </div>
      {(selectedFilters.length > 0 || sort) && (
        <p className="muted small-print">
          {selectedFilters.length > 0 ? `Filters: ${selectedFilters.join(", ")}.` : "Filters: none selected."}{" "}
          {sort ? `Sort: ${SORT_OPTIONS.find((option) => option.value === sort)?.label || sort}.` : "Sort: default."}
        </p>
      )}
      {loading && <p>Loading restaurants...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && cards.length === 0 && <p className="muted">No restaurants returned.</p>}
      <div className="grid cards">{cards}</div>
    </section>
  );
}
