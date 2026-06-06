export const MIN_SEARCH_LENGTH = 3

/** Retourne la query API si ≥ 3 caractères, sinon `undefined` (pas de filtre). */
export function resolveSearchQuery(value: string): string | undefined {
  const trimmed = value.trim()
  return trimmed.length >= MIN_SEARCH_LENGTH ? trimmed : undefined
}

export function searchHint(value: string): string | null {
  const len = value.trim().length
  if (len === 0 || len >= MIN_SEARCH_LENGTH) return null
  return `Saisir au moins ${MIN_SEARCH_LENGTH} caractères pour filtrer`
}
