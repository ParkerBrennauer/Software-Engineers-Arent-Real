/**
 * Total units across all line items (matches how cart quantities work in CartContext).
 * @param {unknown} items
 * @returns {number}
 */
export function getCartTotalQuantity(items) {
  if (!Array.isArray(items)) return 0;
  return items.reduce((sum, i) => {
    const q = Number(i?.quantity);
    if (!Number.isFinite(q) || q <= 0) return sum;
    return sum + q;
  }, 0);
}
