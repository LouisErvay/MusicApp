import type { PageMeta } from '../types'

interface PaginatedResponse<T> extends PageMeta {
  items: T[]
}

export async function fetchAllPages<T>(
  fetchPage: (page: number, size: number) => Promise<PaginatedResponse<T>>,
  size = 100,
): Promise<T[]> {
  const all: T[] = []
  let page = 1
  let pages = 1

  while (page <= pages) {
    const res = await fetchPage(page, size)
    all.push(...res.items)
    pages = res.pages
    page += 1
  }

  return all
}
