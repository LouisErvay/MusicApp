import type {
  Artist,
  ArtistCreate,
  ArtistPage,
  ArtistUpdate,
} from '../types'
import { appendPagination, appendSearchParam } from './query'
import { apiFetch } from './client'

export interface ListArtistsParams {
  page?: number
  size?: number
  username?: string
}

function buildArtistsQuery(params: ListArtistsParams): string {
  const { page = 1, size = 20, username } = params
  const qs = new URLSearchParams()
  appendPagination(qs, page, size)
  appendSearchParam(qs, 'username', username)
  return qs.toString()
}

export function listArtists(params: ListArtistsParams = {}): Promise<ArtistPage> {
  return apiFetch<ArtistPage>(`/artists/?${buildArtistsQuery(params)}`)
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
