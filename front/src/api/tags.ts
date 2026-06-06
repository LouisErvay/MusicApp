import type { Tag, TagCreate, TagPage, TagUpdate } from '../types'
import { apiFetch } from './client'

export function listTags(page = 1, size = 20): Promise<TagPage> {
  return apiFetch<TagPage>(`/tags/?page=${page}&size=${size}`)
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
