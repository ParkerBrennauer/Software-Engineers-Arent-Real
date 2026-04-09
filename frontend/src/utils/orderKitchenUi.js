/** @param {unknown} s */
export function normalizeStatusKey(s) {
  return String(s ?? "")
    .toLowerCase()
    .replace(/_/g, " ")
    .trim();
}

/** Mark ready is meaningful when order is not already terminal / out for pickup. */
export function canShowMarkReady(orderStatus) {
  const n = normalizeStatusKey(orderStatus);
  if (!n) return true;
  if (n.includes("cancel")) return false;
  if (n.includes("picked") || n === "picked up") return false;
  if (n.includes("delivered")) return false;
  if (n.includes("ready") && n.includes("pickup")) return false;
  if (n.includes("ready_for_pickup")) return false;
  return true;
}

/** Assign when there is no driver yet and order is not finished. */
export function canShowAssignDriver(order) {
  const st = normalizeStatusKey(order?.order_status);
  if (st.includes("cancel")) return false;
  if (st.includes("picked") || st === "picked up") return false;
  if (st.includes("delivered")) return false;
  const d = order?.driver;
  if (d != null && String(d).trim() !== "") return false;
  return true;
}

export function canShowRefund(orderStatus) {
  const n = normalizeStatusKey(orderStatus);
  return n.includes("delay") || n.includes("cancel");
}

/** @param {unknown} items */
export function summarizeItems(items) {
  if (!Array.isArray(items)) return "—";
  const parts = items
    .map((it) => {
      if (it && typeof it === "object" && it.item_name != null) return String(it.item_name);
      return null;
    })
    .filter(Boolean);
  if (parts.length === 0) return "—";
  return parts.slice(0, 4).join(", ") + (parts.length > 4 ? "…" : "");
}

/**
 * Unique driver names seen on orders, plus env and manual lists.
 * @param {object[]} orders
 * @param {string[]} manualUsernames
 * @param {string[]} envUsernames
 */
export function mergeDriverCandidates(orders, manualUsernames, envUsernames) {
  const set = new Set();
  for (const u of envUsernames) {
    const t = String(u).trim();
    if (t) set.add(t);
  }
  for (const u of manualUsernames) {
    const t = String(u).trim();
    if (t) set.add(t);
  }
  for (const o of orders) {
    const d = o?.driver;
    if (d != null && String(d).trim() !== "") set.add(String(d).trim());
  }
  return Array.from(set).sort((a, b) => a.localeCompare(b));
}

/**
 * Pick driver with fewest active orders in the current batch (tie-break alphabetically).
 * @param {string[]} candidates
 * @param {object[]} orders
 */
export function pickAutoDriver(candidates, orders) {
  if (!candidates.length) return "";
  const load = new Map();
  for (const c of candidates) load.set(c, 0);
  for (const o of orders) {
    const d = o?.driver;
    if (d != null && load.has(String(d).trim())) {
      const k = String(d).trim();
      load.set(k, (load.get(k) || 0) + 1);
    }
  }
  let best = candidates[0];
  let bestScore = load.get(best) ?? 0;
  for (const c of candidates) {
    const sc = load.get(c) ?? 0;
    if (sc < bestScore || (sc === bestScore && c.localeCompare(best) < 0)) {
      best = c;
      bestScore = sc;
    }
  }
  return best;
}
