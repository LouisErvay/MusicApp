import type {
  Artist,
  ArtistCreate,
  ArtistPage,
  ArtistUpdate,
} from '../types'
import { apiFetch } from './client'

export function listArtists(page = 1, size = 20): Promise<ArtistPage> {
  return apiFetch<ArtistPage>(`/artists/?page=${page}&size=${size}`)
}

export function getArtist(id: number): Promise<Artist> {
  return apiFetch<Artist>(`/artists/${id}`)
}

export function createArtist(payload: ArtistCreate): Promise<Artist> {
  return apiFetch<Artist>('/artists/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function updateArtist(id: number, payload: ArtistUpdate): Promise<Artist> {
  return apiFetch<Artist>(`/artists/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function deleteArtist(id: number): Promise<void> {
  return apiFetch<void>(`/artists/${id}`, { method: 'DELETE' })
}
