/**
 * Normalize place-order API payload for display (handles missing fields).
 * @param {unknown} raw
 * @returns {{ orderIdDisplay: string; costDisplay: string; itemLines: string[] }}
 */
export function getOrderPlacementDetails(raw) {
  const fallbackId = "Unavailable";
  const fallbackCost = "Unavailable";

  if (raw == null || typeof raw !== "object") {
    return { orderIdDisplay: fallbackId, costDisplay: fallbackCost, itemLines: [] };
  }

  const id = /** @type {Record<string, unknown>} */ (raw).id ?? /** @type {Record<string, unknown>} */ (raw).order_id;
  const orderIdDisplay =
    id != null && String(id).trim() !== "" ? String(id).trim() : fallbackId;

  const cost = /** @type {Record<string, unknown>} */ (raw).cost;
  const costNum = Number(cost);
  const costDisplay = Number.isFinite(costNum) ? formatUsd(costNum) : fallbackCost;

  const items = /** @type {Record<string, unknown>} */ (raw).items;
  const itemLines = [];
  if (Array.isArray(items)) {
    for (const entry of items) {
      const label = lineLabelFromItem(entry);
      if (label) itemLines.push(label);
    }
  }

  return { orderIdDisplay, costDisplay, itemLines };
}

/**
 * @param {unknown} item
 * @returns {string}
 */
function lineLabelFromItem(item) {
  if (typeof item === "string" && item.trim()) return item.trim();
  if (item && typeof item === "object") {
    const o = /** @type {Record<string, unknown>} */ (item);
    const name = o.item_name ?? o.name ?? o.title;
    if (typeof name === "string" && name.trim()) return name.trim();
  }
  return "";
}

function formatUsd(n) {
  try {
    return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(n);
  } catch {
    return `$${Number(n).toFixed(2)}`;
  }
}
