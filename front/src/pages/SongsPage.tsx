import { useCallback, useEffect, useMemo, useState } from 'react'
import { listArtists } from '../api/artists'
import {
  createSong,
  createSongsBulk,
  deleteSong,
  getSong,
  listSongs,
  updateSong,
} from '../api/songs'
import { listTags } from '../api/tags'
import { fileDownloadUrl } from '../api/config'
import { Alert } from '../components/Alert'
import { Button } from '../components/Button'
import { IconButton } from '../components/IconButton'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { DataTable } from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { EmptyState } from '../components/EmptyState'
import { Modal } from '../components/Modal'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { SongPlayButton } from '../components/SongPlayButton'
import { SongCreateForm } from '../components/SongCreateForm'
import { SongDuration } from '../components/SongDuration'
import type { SongCreatePayload } from '../components/SongCreateForm'
import { SongForm } from '../components/SongForm'
import type { SongFormSubmitPayload } from '../components/SongForm'
import { TableColumnEntityFilterHeader } from '../components/TableColumnEntityFilterHeader'
import type { EntityFilterOption } from '../components/TableColumnEntityFilterHeader'
import { TableColumnTextFilterHeader } from '../components/TableColumnTextFilterHeader'
import { usePagination } from '../hooks/usePagination'
import type { Song } from '../types'
import { ApiError } from '../types'
import { fetchAllPages } from '../utils/fetchAllPages'
import { formatDate } from '../utils/format'
import { resolveSearchQuery } from '../utils/search'
import './SongsPage.css'

function DownloadIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <path d="M12 3v12" strokeLinecap="round" />
      <path d="M7 10l5 5 5-5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5 19h14" strokeLinecap="round" />
    </svg>
  )
}

function EditIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <path d="M4 20h4l10.5-10.5a2.1 2.1 0 0 0-3-3L5 17v3z" strokeLinejoin="round" />
      <path d="M13.5 6.5l3 3" strokeLinecap="round" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <path d="M4 7h16" strokeLinecap="round" />
      <path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" strokeLinecap="round" />
      <path d="M7 7l1 13a1 1 0 0 0 1 .9h6a1 1 0 0 0 1-.9l1-13" strokeLinejoin="round" />
    </svg>
  )
}

function joinLabels(values: string[] | undefined): string {
  return (values ?? []).filter(Boolean).join('; ') || '—'
}

export function SongsPage() {
  const { page, size, setPage, reset } = usePagination()

  const [data, setData] = useState<Song[]>([])
  const [pages, setPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [appliedName, setAppliedName] = useState<string | undefined>(undefined)
  const [appliedArtistIds, setAppliedArtistIds] = useState<number[]>([])
  const [appliedArtistLabels, setAppliedArtistLabels] = useState<string[]>([])
  const [appliedTagIds, setAppliedTagIds] = useState<number[]>([])
  const [appliedTagLabels, setAppliedTagLabels] = useState<string[]>([])

  const [createOpen, setCreateOpen] = useState(false)
  const [editSong, setEditSong] = useState<Song | null>(null)
  const [editDetail, setEditDetail] = useState<Song | null>(null)
  const [editLoading, setEditLoading] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Song | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const [selectedIds, setSelectedIds] = useState<Set<number>>(() => new Set())

  const hasFilters =
    appliedName !== undefined ||
    appliedArtistIds.length > 0 ||
    appliedTagIds.length > 0

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listSongs({
        page,
        size,
        name: appliedName,
        artistIds: appliedArtistIds,
        tagIds: appliedTagIds,
      })
      setData(res.items)
      setPages(res.pages)
      setTotal(res.total)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors du chargement.')
    } finally {
      setLoading(false)
    }
  }, [page, size, appliedName, appliedArtistIds, appliedTagIds])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    if (!editSong) {
      setEditDetail(null)
      setEditLoading(false)
      return
    }

    let cancelled = false
    setEditLoading(true)
    setEditDetail(null)

    void getSong(editSong.id)
      .then((song) => {
        if (!cancelled) setEditDetail(song)
      })
      .catch((err) => {
        if (!cancelled) {
          setEditSong(null)
          setError(err instanceof ApiError ? err.message : 'Erreur lors du chargement de la chanson.')
        }
      })
      .finally(() => {
        if (!cancelled) setEditLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [editSong])

  const applyNameFilter = useCallback(
    (value: string) => {
      setAppliedName(resolveSearchQuery(value))
      reset()
      setPage(1)
    },
    [reset, setPage],
  )

  const applyArtistFilter = useCallback(
    (ids: number[], labels: string[]) => {
      setAppliedArtistIds(ids)
      setAppliedArtistLabels(labels)
      reset()
      setPage(1)
    },
    [reset, setPage],
  )

  const applyTagFilter = useCallback(
    (ids: number[], labels: string[]) => {
      setAppliedTagIds(ids)
      setAppliedTagLabels(labels)
      reset()
      setPage(1)
    },
    [reset, setPage],
  )

  const fetchArtistOptions = useCallback(async (search?: string): Promise<EntityFilterOption[]> => {
    const items = search
      ? (await listArtists({ username: search, size: 100 })).items
      : await fetchAllPages((p, s) => listArtists({ page: p, size: s }))
    return items.map((artist) => ({ id: artist.id, label: artist.username }))
  }, [])

  const fetchTagOptions = useCallback(async (search?: string): Promise<EntityFilterOption[]> => {
    const items = search
      ? (await listTags({ name: search, size: 100 })).items
      : await fetchAllPages((p, s) => listTags({ page: p, size: s }))
    return items.map((tag) => ({ id: tag.id, label: tag.name }))
  }, [])

  function clearFilters() {
    setAppliedName(undefined)
    setAppliedArtistIds([])
    setAppliedArtistLabels([])
    setAppliedTagIds([])
    setAppliedTagLabels([])
    reset()
    setPage(1)
  }

  async function reloadAfterMutation() {
    await load()
  }

  async function handleCreate({ entries, artists, tags }: SongCreatePayload) {
    setSubmitting(true)
    setError(null)
    try {
      if (entries.length === 1) {
        await createSong(entries[0].name, entries[0].file, { artists, tags })
        setSuccess('Chanson ajoutée.')
      } else {
        const files = entries.map((e) => e.file)
        const items = entries.map((entry, index) => ({
          name: entry.name,
          file_index: index,
          artist: artists,
          tag: tags,
        }))
        const res = await createSongsBulk(items, files)
        setSuccess(`${res.created} chanson${res.created > 1 ? 's' : ''} ajoutée${res.created > 1 ? 's' : ''}.`)
      }
      setCreateOpen(false)
      reset()
      setPage(1)
      await reloadAfterMutation()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors de la création.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleEdit({ name, artists, tags }: SongFormSubmitPayload) {
    if (!editSong) return
    setSubmitting(true)
    setError(null)
    try {
      await updateSong(editSong.id, {
        name,
        ...(artists !== undefined ? { artist: artists } : {}),
        ...(tags !== undefined ? { tag: tags } : {}),
      })
      setEditSong(null)
      setSuccess('Chanson mise à jour.')
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors de la mise à jour.')
    } finally {
      setSubmitting(false)
    }
  }

  const toggleSelection = useCallback((id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const toggleAllOnPage = useCallback(() => {
    const pageIds = data.map((s) => s.id)
    setSelectedIds((prev) => {
      const allSelected = pageIds.length > 0 && pageIds.every((id) => prev.has(id))
      const next = new Set(prev)
      if (allSelected) {
        pageIds.forEach((id) => next.delete(id))
      } else {
        pageIds.forEach((id) => next.add(id))
      }
      return next
    })
  }, [data])

  const handleDownload = useCallback((song: Song) => {
    const link = document.createElement('a')
    link.href = fileDownloadUrl(song.file_id)
    link.download = song.file?.name ?? `${song.name}.audio`
    link.rel = 'noopener'
    link.click()
  }, [])

  async function handleDelete() {
    if (!deleteTarget) return
    setSubmitting(true)
    setError(null)
    try {
      await deleteSong(deleteTarget.id)
      setDeleteTarget(null)
      setSuccess('Chanson supprimée.')
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors de la suppression.')
    } finally {
      setSubmitting(false)
    }
  }

  const allOnPageSelected =
    data.length > 0 && data.every((song) => selectedIds.has(song.id))
  const someOnPageSelected = data.some((song) => selectedIds.has(song.id))

  const columns = useMemo<Column<Song>[]>(
    () => [
      {
        key: 'play',
        header: '',
        className: 'col-play',
        render: (row) => <SongPlayButton song={row} queue={data} />,
      },
      {
        key: 'select',
        header: (
          <input
            type="checkbox"
            className="songs-page__checkbox"
            checked={allOnPageSelected}
            ref={(el) => {
              if (el) el.indeterminate = someOnPageSelected && !allOnPageSelected
            }}
            onChange={toggleAllOnPage}
            aria-label="Tout sélectionner sur cette page"
          />
        ),
        className: 'col-checkbox',
        render: (row) => (
          <input
            type="checkbox"
            className="songs-page__checkbox"
            checked={selectedIds.has(row.id)}
            onChange={() => toggleSelection(row.id)}
            aria-label={`Sélectionner ${row.name}`}
          />
        ),
      },
      {
        key: 'name',
        header: (
          <TableColumnTextFilterHeader
            title="Nom"
            appliedLabel={appliedName}
            onApply={applyNameFilter}
          />
        ),
        className: 'col-filter',
        render: (row) => (
          <strong className="data-table__cell-truncate" title={row.name}>
            {row.name}
          </strong>
        ),
      },
      {
        key: 'artists',
        header: (
          <TableColumnEntityFilterHeader
            title="Artistes"
            appliedIds={appliedArtistIds}
            appliedLabels={appliedArtistLabels}
            onApply={applyArtistFilter}
            fetchOptions={fetchArtistOptions}
          />
        ),
        className: 'col-filter',
        render: (row) => {
          const text = joinLabels(row.artist)
          return (
            <span className="data-table__cell-truncate muted" title={text}>
              {text}
            </span>
          )
        },
      },
      {
        key: 'tags',
        header: (
          <TableColumnEntityFilterHeader
            title="Tags"
            appliedIds={appliedTagIds}
            appliedLabels={appliedTagLabels}
            onApply={applyTagFilter}
            fetchOptions={fetchTagOptions}
          />
        ),
        className: 'col-filter',
        render: (row) => {
          const text = joinLabels(row.tag)
          return (
            <span className="data-table__cell-truncate muted" title={text}>
              {text}
            </span>
          )
        },
      },
      {
        key: 'duration',
        header: 'Durée',
        render: (row) => <SongDuration fileId={row.file_id} />,
      },
      {
        key: 'updated',
        header: 'Modifié',
        render: (row) => <span className="muted">{formatDate(row.updated_at)}</span>,
      },
      {
        key: 'actions',
        header: 'Actions',
        className: 'actions',
        render: (row) => (
          <div className="songs-page__row-actions">
            <IconButton label="Télécharger" onClick={() => handleDownload(row)}>
              <DownloadIcon />
            </IconButton>
            <IconButton label="Modifier" onClick={() => setEditSong(row)}>
              <EditIcon />
            </IconButton>
            <IconButton variant="danger" label="Supprimer" onClick={() => setDeleteTarget(row)}>
              <TrashIcon />
            </IconButton>
          </div>
        ),
      },
    ],
    [
      allOnPageSelected,
      someOnPageSelected,
      selectedIds,
      data,
      appliedName,
      appliedArtistIds,
      appliedArtistLabels,
      appliedTagIds,
      appliedTagLabels,
      applyNameFilter,
      applyArtistFilter,
      applyTagFilter,
      fetchArtistOptions,
      fetchTagOptions,
      toggleAllOnPage,
      toggleSelection,
      handleDownload,
    ],
  )

  const emptyDescription = hasFilters
    ? 'Aucune chanson ne correspond aux critères de recherche.'
    : 'Commencez par importer un fichier audio.'

  return (
    <div className="songs-page">
      <PageHeader
        title="Chansons"
        description="Gérez le catalogue audio : recherche dans le tableau, upload, renommage et suppression."
        actions={
          <Button onClick={() => setCreateOpen(true)}>+ Ajouter des chansons</Button>
        }
      />

      {error ? (
        <Alert variant="error" onDismiss={() => setError(null)}>
          {error}
        </Alert>
      ) : null}
      {success ? (
        <Alert variant="success" onDismiss={() => setSuccess(null)}>
          {success}
        </Alert>
      ) : null}

      {!loading && data.length === 0 ? (
        <EmptyState
          icon="♫"
          title="Aucune chanson"
          description={emptyDescription}
          action={
            hasFilters ? (
              <Button variant="secondary" onClick={clearFilters}>
                Réinitialiser les filtres
              </Button>
            ) : (
              <Button onClick={() => setCreateOpen(true)}>Ajouter des chansons</Button>
            )
          }
        />
      ) : (
        <>
          <DataTable
            className="data-table-wrap--filters-open"
            columns={columns}
            data={data}
            keyExtractor={(r) => r.id}
            loading={loading}
          />
          <Pagination page={page} pages={pages} pageSize={size} total={total} onPageChange={setPage} />
        </>
      )}

      <Modal
        open={createOpen}
        title="Nouvelles chansons"
        wide
        onClose={() => setCreateOpen(false)}
      >
        <SongCreateForm
          loading={submitting}
          onSubmit={(payload) => void handleCreate(payload)}
          onCancel={() => setCreateOpen(false)}
        />
      </Modal>

      <Modal
        open={editSong !== null}
        title="Modifier la chanson"
        onClose={() => setEditSong(null)}
      >
        {editSong && editDetail ? (
          <SongForm
            initialName={editDetail.name}
            initialArtists={editDetail.artist ?? []}
            initialTags={editDetail.tag ?? []}
            requireFile={false}
            loading={submitting || editLoading}
            onSubmit={(payload) => void handleEdit(payload)}
            onCancel={() => setEditSong(null)}
          />
        ) : editSong ? (
          <p className="muted">Chargement…</p>
        ) : null}
      </Modal>

      <ConfirmDialog
        open={deleteTarget !== null}
        title="Supprimer la chanson"
        message={`Supprimer « ${deleteTarget?.name ?? ''} » ? Cette action est irréversible.`}
        loading={submitting}
        onConfirm={() => void handleDelete()}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
