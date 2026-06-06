import type { Song, SongPage, SongUpdate } from '../types'
import { apiFetch, apiFetchForm } from './client'

export function listSongs(page = 1, size = 20): Promise<SongPage> {
  return apiFetch<SongPage>(`/songs/?page=${page}&size=${size}`)
}

export function getSong(id: number): Promise<Song> {
  return apiFetch<Song>(`/songs/${id}`)
}

export function createSong(name: string, file: File): Promise<Song> {
  const form = new FormData()
  form.append('name', name)
  form.append('file', file)
  return apiFetchForm<Song>('/songs/', form)
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
