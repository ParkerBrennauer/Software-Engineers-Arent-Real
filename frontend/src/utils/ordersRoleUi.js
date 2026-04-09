/**
 * Roles the Orders & Tracking UI understands (matches AuthContext-derived `user.role`).
 * @typedef {'customer' | 'driver' | 'owner' | 'staff'} OrdersUiRole
 */

const KNOWN_ORDERS_ROLES = new Set(["customer", "driver", "owner", "staff"]);

/**
 * @param {unknown} user
 * @returns {OrdersUiRole | null} Null when role is missing or not a known orders role (fail-safe).
 */
export function resolveOrdersUiRole(user) {
  if (!user || user.requires2FA) return null;
  const r = user.role;
  if (typeof r !== "string") return null;
  const n = r.trim().toLowerCase();
  if (!n || !KNOWN_ORDERS_ROLES.has(n)) return null;
  return /** @type {OrdersUiRole} */ (n);
}
