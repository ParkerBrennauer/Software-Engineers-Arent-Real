/**
 * @param {unknown} dietary
 * @returns {string[]} Human-readable tags for true restriction flags.
 */
export function dietaryTags(dietary) {
  if (!dietary || typeof dietary !== "object") return [];
  return Object.entries(dietary)
    .filter(([, v]) => v === true)
    .map(([k]) => k.replace(/_/g, " "));
}
