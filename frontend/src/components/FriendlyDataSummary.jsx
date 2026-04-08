import React from "react";

function humanizeKey(key) {
  if (typeof key !== "string") return String(key);
  return key
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^\w/, (c) => c.toUpperCase());
}

function formatLeaf(key, value) {
  if (value === null || value === undefined) return "—";
  const k = String(key).toLowerCase();
  if (typeof value === "number" && (k.includes("cost") || k.includes("price") || k.includes("total") || k.includes("amount"))) {
    try {
      return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(value);
    } catch {
      return `$${Number(value).toFixed(2)}`;
    }
  }
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return String(value);
  const s = String(value);
  return s.length > 400 ? `${s.slice(0, 400)}…` : s;
}

function renderValue(data, depth) {
  if (data === null || data === undefined) return <span className="muted">—</span>;
  if (typeof data === "string" || typeof data === "number" || typeof data === "boolean") {
    return <span>{formatLeaf("value", data)}</span>;
  }
  if (depth > 8) return <span className="muted">…</span>;
  if (Array.isArray(data)) {
    if (data.length === 0) return <p className="muted">Nothing here yet.</p>;
    const allObjects =
      data.every((x) => x && typeof x === "object" && !Array.isArray(x)) && data.length > 0;
    if (allObjects) {
      return (
        <ul className="app-data-summary__card-list">
          {data.map((item, i) => (
            <li key={i} className="panel app-data-summary__item-card">
              {renderObject(item, depth + 1)}
            </li>
          ))}
        </ul>
      );
    }
    return (
      <ul className="list-compact app-data-summary__inline-list">
        {data.map((item, i) => (
          <li key={i}>{renderValue(item, depth + 1)}</li>
        ))}
      </ul>
    );
  }
  if (typeof data === "object") {
    return renderObject(data, depth);
  }
  return <span>{String(data)}</span>;
}

function renderObject(obj, depth) {
  const entries = Object.entries(obj).filter(([k]) => k !== "__proto__" && k !== "constructor");
  if (entries.length === 0) {
    return <p className="muted">No additional details.</p>;
  }
  return (
    <dl className="app-data-summary__dl">
      {entries.map(([k, v]) => (
        <div key={k} className="app-data-summary__row">
          <dt>{humanizeKey(k)}</dt>
          <dd>
            {v !== null && typeof v === "object" ? (
              renderValue(v, depth + 1)
            ) : (
              <span>{formatLeaf(k, v)}</span>
            )}
          </dd>
        </div>
      ))}
    </dl>
  );
}

/**
 * Presents structured API data in a readable layout (replaces raw JSON dumps).
 */
export default function FriendlyDataSummary({ data, title = "Summary", onDismiss }) {
  if (data === null || data === undefined) return null;

  return (
    <section className="panel app-data-summary" role="region" aria-label={title}>
      <div className="app-data-summary__header">
        <h3 className="app-data-summary__title">{title}</h3>
        {typeof onDismiss === "function" && (
          <button type="button" className="app-data-summary__dismiss" onClick={onDismiss}>
            Dismiss
          </button>
        )}
      </div>
      <div className="app-data-summary__body">{renderValue(data, 0)}</div>
    </section>
  );
}
