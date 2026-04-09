/**
 * Persists the account type chosen at registration so login can resolve role when the
 * backend login payload does not include role (see backend UserResponse schema).
 */
const STORAGE_KEY = "frontend-auth-role-hint-v1";

/**
 * @param {string} username
 * @returns {string | null}
 */
export function readRoleHint(username) {
  if (!username || typeof username !== "string") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const all = JSON.parse(raw);
    const v = all[username];
    if (typeof v !== "string" || !v.trim()) return null;
    return v.trim().toLowerCase();
  } catch {
    return null;
  }
}

/**
 * @param {string} username
 * @param {string} role
 */
export function writeRoleHint(username, role) {
  if (!username || typeof username !== "string" || !role || typeof role !== "string") return;
  const normalized = role.trim().toLowerCase();
  if (!normalized) return;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const all = raw ? JSON.parse(raw) : {};
    all[username] = normalized;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  } catch {
    // ignore quota / parse errors
  }
}
