import { api } from "../api/client";

/**
 * Resolves which venue the logged-in owner/staff account may administer by probing
 * existing restaurant administration endpoints. The backend does not expose restaurant_id
 * on public user routes; permission checks on orders are the available signal.
 *
 * @param {Array<Record<string, unknown>>} restaurants normalized list from GET /restaurants
 * @returns {Promise<Record<string, unknown> | null>} first matching restaurant row, or null
 */
export async function resolveVenueViaAdminOrdersProbe(restaurants) {
  if (!Array.isArray(restaurants) || restaurants.length === 0) return null;

  const rows = restaurants.filter((r) => r?.restaurant_id != null);
  const ids = [...new Set(rows.map((r) => Number(r.restaurant_id)).filter((n) => Number.isInteger(n) && n > 0))];
  ids.sort((a, b) => a - b);

  /** @type {Map<number, Record<string, unknown>>} */
  const byId = new Map();
  for (const r of rows) {
    const id = Number(r.restaurant_id);
    if (Number.isInteger(id) && id > 0 && !byId.has(id)) byId.set(id, r);
  }

  const BATCH = 6;

  for (let i = 0; i < ids.length; i += BATCH) {
    const chunk = ids.slice(i, i + BATCH);
    /** @type {Promise<{ id: number, row: Record<string, unknown> | null, fatal?: boolean }>[]} */
    const tasks = chunk.map(async (id) => {
      try {
        await api.restaurantAdministration.orders(String(id));
        return { id, row: byId.get(id) || { restaurant_id: id } };
      } catch (e) {
        const msg = String(e?.message || "");
        if (/does not have permission/i.test(msg)) {
          return { id, row: null };
        }
        if (/not authenticated|401/i.test(msg)) {
          return { id, row: null, fatal: true };
        }
        if (/not found/i.test(msg) && /restaurant/i.test(msg)) {
          return { id, row: null };
        }
        return { id, row: null, fatal: true };
      }
    });

    const results = await Promise.all(tasks);
    if (results.some((r) => r.fatal)) {
      return null;
    }
    const hit = results.find((r) => r.row != null);
    if (hit?.row) return hit.row;
  }

  return null;
}
