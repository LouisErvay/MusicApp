import type { SongUpdate } from '../types'

interface SongEditState {
  name: string
  artists: string[]
  tags: string[]
}

interface EntityNameMaps {
  artistNameToId: Map<string, number>
  tagNameToId: Map<string, number>
}

export function buildSongUpdatePayload(
  initial: SongEditState,
  updated: { name: string; artists?: string[]; tags?: string[] },
  maps: EntityNameMaps,
): SongUpdate {
  const payload: SongUpdate = {}
  const trimmedName = updated.name.trim()

  if (trimmedName !== initial.name) {
    payload.name = trimmedName
  }

  if (updated.artists !== undefined) {
    const initialSet = new Set(initial.artists)
    const newSet = new Set(updated.artists)
    const artistAdd = updated.artists.filter((name) => !initialSet.has(name))
    const artistDelete = initial.artists
      .filter((name) => !newSet.has(name))
      .map((name) => maps.artistNameToId.get(name))
      .filter((id): id is number => id !== undefined)

    if (artistAdd.length > 0) payload.artist_add = artistAdd
    if (artistDelete.length > 0) payload.artist_delete = artistDelete
  }

  if (updated.tags !== undefined) {
    const initialSet = new Set(initial.tags)
    const newSet = new Set(updated.tags)
    const tagAdd = updated.tags.filter((name) => !initialSet.has(name))
    const tagDelete = initial.tags
      .filter((name) => !newSet.has(name))
      .map((name) => maps.tagNameToId.get(name))
      .filter((id): id is number => id !== undefined)

    if (tagAdd.length > 0) payload.tag_add = tagAdd
    if (tagDelete.length > 0) payload.tag_delete = tagDelete
  }

  return payload
}

export function buildEntityNameMaps(
  artists: { id: number; username: string }[],
  tags: { id: number; name: string }[],
): EntityNameMaps {
  return {
    artistNameToId: new Map(artists.map((artist) => [artist.username, artist.id])),
    tagNameToId: new Map(tags.map((tag) => [tag.name, tag.id])),
  }
}
