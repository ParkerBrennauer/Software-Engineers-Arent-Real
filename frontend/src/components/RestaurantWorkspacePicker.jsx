import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { normalizeApiArray } from "../utils/normalizeApiArray";
import { buildRestaurantDisplayLabel } from "../state/RestaurantWorkspaceContext";

/**
 * Modal to pick a venue from GET /restaurants (no owner filter on the API — user chooses their location).
 */
export default function RestaurantWorkspacePicker({ open, onClose, onSelect, mustChoose }) {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [query, setQuery] = useState("");

  useEffect(() => {
    if (!open) return;
    let active = true;
    setLoadError("");
    setLoading(true);
    (async () => {
      try {
        const data = await api.restaurants.getAll();
        if (!active) return;
        setList(normalizeApiArray(data).filter((r) => r?.restaurant_id != null));
      } catch (e) {
        if (active) setLoadError(e?.message || "Could not load restaurants.");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [open]);

  useEffect(() => {
    if (!open) setQuery("");
  }, [open]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return list;
    return list.filter((r) => {
      const id = String(r.restaurant_id ?? "");
      const cuisine = String(r.cuisine ?? "").toLowerCase();
      return id.includes(q) || cuisine.includes(q);
    });
  }, [list, query]);

  if (!open) return null;

  function handleBackdropClick() {
    if (!mustChoose) onClose();
  }

  function handleKeyDown(e) {
    if (e.key === "Escape" && !mustChoose) onClose();
  }

  return (
    <div
      className="restaurant-workspace-picker-backdrop"
      role="presentation"
      onClick={handleBackdropClick}
      onKeyDown={handleKeyDown}
    >
      <div
        className="restaurant-workspace-picker panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="restaurant-workspace-picker-title"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="restaurant-workspace-picker-title" className="restaurant-workspace-picker__title">
          Which venue do you manage?
        </h2>
        <p className="muted small-print restaurant-workspace-picker__lede">
          We&apos;ll use this for your kitchen queue, reports, and promos so you don&apos;t have to enter it each time.
          You can change it later from the bar at the top.
        </p>
        <div className="row restaurant-workspace-picker__search">
          <input
            type="search"
            placeholder="Search by number or cuisine"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search venues"
            autoFocus
          />
        </div>
        {loading && <p className="muted">Loading venues…</p>}
        {loadError && (
          <p className="error app-inline-alert" role="alert">
            {loadError}
          </p>
        )}
        {!loading && !loadError && filtered.length === 0 && (
          <p className="muted">No venues match your search.</p>
        )}
        {!loading && !loadError && filtered.length > 0 && (
          <ul className="restaurant-workspace-picker__list" data-testid="restaurant-workspace-picker-list">
            {filtered.map((r) => {
              const id = r.restaurant_id;
              const label = buildRestaurantDisplayLabel(r);
              return (
                <li key={String(id)}>
                  <button
                    type="button"
                    className="restaurant-workspace-picker__row"
                    onClick={() => onSelect(r)}
                  >
                    <span className="restaurant-workspace-picker__row-title">{label}</span>
                    {r.avg_ratings != null && r.avg_ratings !== "" && (
                      <span className="muted small-print">
                        Rating {Number(r.avg_ratings).toFixed(1)}
                      </span>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
        {!mustChoose && (
          <div className="restaurant-workspace-picker__footer">
            <button type="button" className="kitchen-btn-secondary" onClick={onClose}>
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
