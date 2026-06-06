import { resolveSearchQuery } from '../utils/search'

export function appendPagination(
  qs: URLSearchParams,
  page: number,
  size: number,
): void {
  qs.set('page', String(page))
  qs.set('size', String(size))
}

/** Ajoute le paramètre seulement si la valeur fait ≥ 3 caractères (après trim). */
export function appendSearchParam(
  qs: URLSearchParams,
  key: string,
  value?: string,
): void {
  const query = value ? resolveSearchQuery(value) : undefined
  if (query) qs.set(key, query)
}
