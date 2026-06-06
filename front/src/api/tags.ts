import type { Tag, TagCreate, TagPage, TagUpdate } from '../types'
import { appendPagination, appendSearchParam } from './query'
import { apiFetch } from './client'

export interface ListTagsParams {
  page?: number
  size?: number
  name?: string
}

function buildTagsQuery(params: ListTagsParams): string {
  const { page = 1, size = 20, name } = params
  const qs = new URLSearchParams()
  appendPagination(qs, page, size)
  appendSearchParam(qs, 'name', name)
  return qs.toString()
}

export function listTags(params: ListTagsParams = {}): Promise<TagPage> {
  return apiFetch<TagPage>(`/tags/?${buildTagsQuery(params)}`)
}

export function getTag(id: number): Promise<Tag> {
  return apiFetch<Tag>(`/tags/${id}`)
}

export function createTag(payload: TagCreate): Promise<Tag> {
  return apiFetch<Tag>('/tags/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function updateTag(id: number, payload: TagUpdate): Promise<Tag> {
  return apiFetch<Tag>(`/tags/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function deleteTag(id: number): Promise<void> {
  return apiFetch<void>(`/tags/${id}`, { method: 'DELETE' })
}
