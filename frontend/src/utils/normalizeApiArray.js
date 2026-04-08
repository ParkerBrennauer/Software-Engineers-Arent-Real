/** Normalize API payloads that may be an array or a keyed object. */
export function normalizeApiArray(data) {
  if (Array.isArray(data)) return data;
  if (data && typeof data === "object") return Object.values(data);
  return [];
}
