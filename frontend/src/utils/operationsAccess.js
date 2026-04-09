/** Roles that may use restaurant administration tooling in Operations. */
const OPERATIONS_CONTENT_ROLES = new Set(["owner", "staff", "admin"]);

/**
 * @param {unknown} role
 * @returns {boolean}
 */
export function canViewOperationsContent(role) {
  if (role == null || typeof role !== "string") return false;
  const normalized = role.trim().toLowerCase();
  if (!normalized) return false;
  return OPERATIONS_CONTENT_ROLES.has(normalized);
}
