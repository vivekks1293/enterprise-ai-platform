/** Generates a RFC4122-ish unique id using the platform crypto API. */
export function generateId(): string {
  return crypto.randomUUID();
}
