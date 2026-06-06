import type { Song, SongBulkCreateItem, SongBulkRead, SongPage, SongUpdate } from '../types'
import { apiFetch, apiFetchForm } from './client'

export interface ListSongsParams {
  page?: number
  size?: number
  artistIds?: number[]
  tagIds?: number[]
}

function buildSongsQuery(params: ListSongsParams): string {
  const { page = 1, size = 20, artistIds = [], tagIds = [] } = params
  const qs = new URLSearchParams()
  qs.set('page', String(page))
  qs.set('size', String(size))
  for (const id of artistIds) qs.append('artist_id', String(id))
  for (const id of tagIds) qs.append('tag_id', String(id))
  return qs.toString()
}

export function listSongs(params: ListSongsParams = {}): Promise<SongPage> {
  return apiFetch<SongPage>(`/songs/?${buildSongsQuery(params)}`)
}

export function getSong(id: number): Promise<Song> {
  return apiFetch<Song>(`/songs/${id}`)
}

export interface CreateSongOptions {
  artists?: string[]
  tags?: string[]
}

export function createSong(
  name: string,
  file: File,
  options: CreateSongOptions = {},
): Promise<Song> {
  const form = new FormData()
  form.append('name', name)
  form.append('file', file)
  for (const artist of options.artists ?? []) form.append('artist', artist)
  for (const tag of options.tags ?? []) form.append('tag', tag)
  return apiFetchForm<Song>('/songs/', form)
}

export function createSongsBulk(
  items: SongBulkCreateItem[],
  files: File[],
): Promise<SongBulkRead> {
  const form = new FormData()
  form.append('items', JSON.stringify(items))
  for (const file of files) form.append('files', file)
  return apiFetchForm<SongBulkRead>('/songs/bulk', form)
}

export function updateSong(id: number, payload: SongUpdate): Promise<Song> {
  return apiFetch<Song>(`/songs/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function deleteSong(id: number): Promise<void> {
  return apiFetch<void>(`/songs/${id}`, { method: 'DELETE' })
}
