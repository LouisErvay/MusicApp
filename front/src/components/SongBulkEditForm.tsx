import { useCallback, useState } from 'react'
import { listArtists } from '../api/artists'
import { listTags } from '../api/tags'
import { Button } from './Button'
import { EntityIdListInput } from './EntityIdListInput'
import { StringListInput } from './StringListInput'
import type { EntityFilterOption } from './TableColumnEntityFilterHeader'

export interface SongBulkEditSubmitPayload {
  artist_add?: string[]
  tag_add?: string[]
  artist_delete?: number[]
  tag_delete?: number[]
}

interface SongBulkEditFormProps {
  selectedCount: number
  loading?: boolean
  onSubmit: (payload: SongBulkEditSubmitPayload) => void
  onCancel?: () => void
}

export function SongBulkEditForm({
  selectedCount,
  loading = false,
  onSubmit,
  onCancel,
}: SongBulkEditFormProps) {
  const [artistAdd, setArtistAdd] = useState<string[]>([])
  const [tagAdd, setTagAdd] = useState<string[]>([])
  const [artistDeleteIds, setArtistDeleteIds] = useState<number[]>([])
  const [artistDeleteLabels, setArtistDeleteLabels] = useState<string[]>([])
  const [tagDeleteIds, setTagDeleteIds] = useState<number[]>([])
  const [tagDeleteLabels, setTagDeleteLabels] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  const fetchArtistSuggestions = useCallback(
    (query: string) =>
      listArtists({ username: query, size: 20 }).then((res) =>
        res.items.map((artist) => artist.username),
      ),
    [],
  )

  const fetchTagSuggestions = useCallback(
    (query: string) =>
      listTags({ name: query, size: 20 }).then((res) => res.items.map((tag) => tag.name)),
    [],
  )

  const fetchArtistOptions = useCallback(
    async (search?: string): Promise<EntityFilterOption[]> => {
      const res = await listArtists({ username: search, size: 100 })
      return res.items.map((artist) => ({ id: artist.id, label: artist.username }))
    },
    [],
  )

  const fetchTagOptions = useCallback(async (search?: string): Promise<EntityFilterOption[]> => {
    const res = await listTags({ name: search, size: 100 })
    return res.items.map((tag) => ({ id: tag.id, label: tag.name }))
  }, [])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    const payload: SongBulkEditSubmitPayload = {}
    if (artistAdd.length > 0) payload.artist_add = artistAdd
    if (tagAdd.length > 0) payload.tag_add = tagAdd
    if (artistDeleteIds.length > 0) payload.artist_delete = artistDeleteIds
    if (tagDeleteIds.length > 0) payload.tag_delete = tagDeleteIds

    if (Object.keys(payload).length === 0) {
      setError('Indiquez au moins une modification.')
      return
    }

    setError(null)
    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="entity-form">
      <p className="muted">
        {selectedCount} chanson{selectedCount > 1 ? 's' : ''} sélectionnée
        {selectedCount > 1 ? 's' : ''}. Les ajouts et suppressions seront appliqués à chacune.
      </p>
      {error ? <p className="entity-form__error">{error}</p> : null}
      <StringListInput
        label="Ajouter des artistes"
        values={artistAdd}
        onChange={setArtistAdd}
        placeholder="Ex. Daft Punk"
        disabled={loading}
        fetchSuggestions={fetchArtistSuggestions}
      />
      <StringListInput
        label="Ajouter des tags"
        values={tagAdd}
        onChange={setTagAdd}
        placeholder="Ex. electro"
        disabled={loading}
        fetchSuggestions={fetchTagSuggestions}
      />
      <EntityIdListInput
        label="Retirer des artistes"
        selectedIds={artistDeleteIds}
        selectedLabels={artistDeleteLabels}
        onChange={(ids, labels) => {
          setArtistDeleteIds(ids)
          setArtistDeleteLabels(labels)
        }}
        placeholder="Rechercher un artiste…"
        disabled={loading}
        fetchOptions={fetchArtistOptions}
      />
      <EntityIdListInput
        label="Retirer des tags"
        selectedIds={tagDeleteIds}
        selectedLabels={tagDeleteLabels}
        onChange={(ids, labels) => {
          setTagDeleteIds(ids)
          setTagDeleteLabels(labels)
        }}
        placeholder="Rechercher un tag…"
        disabled={loading}
        fetchOptions={fetchTagOptions}
      />
      <div className="entity-form__actions">
        {onCancel ? (
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Annuler
          </Button>
        ) : null}
        <Button type="submit" loading={loading}>
          Appliquer
        </Button>
      </div>
    </form>
  )
}
