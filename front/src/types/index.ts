export interface PageMeta {
  total: number
  page: number
  size: number
  pages: number
}

export interface FileRead {
  id: string
  name: string
  relative_path: string
  size: number
  mime_type: string | null
  checksum_sha256: string | null
  created_at: string
  updated_at: string
}

export interface Song {
  id: number
  name: string
  file_id: string
  updated_at: string
  file: FileRead | null
  artist?: string[]
  tag?: string[]
}

export interface SongPage extends PageMeta {
  items: Song[]
}

export interface SongUpdate {
  name?: string
  artist?: string[]
  tag?: string[]
}

export interface SongBulkCreateItem {
  name: string
  file_index: number
  artist: string[]
  tag: string[]
}

export interface SongBulkRead {
  items: Song[]
  created: number
}

export interface Artist {
  id: number
  username: string
  updated_at: string
}

export interface ArtistPage extends PageMeta {
  items: Artist[]
}

export interface ArtistCreate {
  username: string
}

export interface ArtistUpdate {
  username?: string
}

export interface Tag {
  id: number
  name: string
  updated_at: string
}

export interface TagPage extends PageMeta {
  items: Tag[]
}

export interface TagCreate {
  name: string
}

export interface TagUpdate {
  name?: string
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}
