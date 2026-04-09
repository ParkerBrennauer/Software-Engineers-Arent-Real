/**
 * Per-username persisted venue choice for owner/staff workflows.
 * The backend omits role and restaurant_id on `/users/login` and `/users/current-user`, so the app
 * may auto-detect venue via administration order checks, then caches the choice here for refresh-safe UX.
 */
const STORAGE_KEY = "frontend-restaurant-workspace-by-user-v1";

/**
 * @param {string} username
 * @returns {{ restaurantId: number, label: string, cuisine: string } | null}
 */
export function readLinkedRestaurant(username) {
  if (!username || typeof username !== "string") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const all = JSON.parse(raw);
    const entry = all[username];
    if (!entry || typeof entry !== "object") return null;
    const id = Number(entry.restaurantId);
    if (!Number.isInteger(id) || id <= 0) return null;
    return {
      restaurantId: id,
      label: typeof entry.label === "string" && entry.label.trim() ? entry.label.trim() : `Restaurant ${id}`,
      cuisine: typeof entry.cuisine === "string" ? entry.cuisine : "",
    };
  } catch {
    return null;
  }
}

/**
 * @param {string} username
 * @param {{ restaurantId: number, label: string, cuisine?: string }} payload
 */
export function writeLinkedRestaurant(username, payload) {
  if (!username || typeof username !== "string") return;
  const id = Number(payload.restaurantId);
  if (!Number.isInteger(id) || id <= 0) return;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const all = raw ? JSON.parse(raw) : {};
    all[username] = {
      restaurantId: id,
      label: typeof payload.label === "string" && payload.label.trim() ? payload.label.trim() : `Restaurant ${id}`,
      cuisine: typeof payload.cuisine === "string" ? payload.cuisine : "",
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  } catch {
    // ignore quota / parse errors
  }
}

/** @param {string} username */
export function clearLinkedRestaurant(username) {
  if (!username || typeof username !== "string") return;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const all = JSON.parse(raw);
    if (all && typeof all === "object") {
      delete all[username];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
    }
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }
}
