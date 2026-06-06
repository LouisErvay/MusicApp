import { useCallback, useEffect, useMemo, useState } from 'react'
import { listArtists } from '../api/artists'
import {
  createSong,
  createSongsBulk,
  deleteSong,
  listSongs,
  updateSong,
} from '../api/songs'
import { listTags } from '../api/tags'
import { Alert } from '../components/Alert'
import { AudioPlayer } from '../components/AudioPlayer'
import { Button } from '../components/Button'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { DataTable } from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { EmptyState } from '../components/EmptyState'
import { FilterCheckboxList } from '../components/FilterCheckboxList'
import { Modal } from '../components/Modal'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { SearchInput } from '../components/SearchInput'
import { SongCreateForm } from '../components/SongCreateForm'
import type { SongCreatePayload } from '../components/SongCreateForm'
import { SongForm } from '../components/SongForm'
import { usePagination } from '../hooks/usePagination'
import { useSearchQuery } from '../hooks/useSearchQuery'
import type { Artist, Song, Tag } from '../types'
import { ApiError } from '../types'
import { fetchAllPages } from '../utils/fetchAllPages'
import { formatBytes, formatDate } from '../utils/format'
import './SongsPage.css'

export function SongsPage() {
  const { page, size, setPage, reset } = usePagination()
  const songSearch = useSearchQuery()
  const artistSearch = useSearchQuery()
  const tagSearch = useSearchQuery()

  const [data, setData] = useState<Song[]>([])
  const [pages, setPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [filterArtists, setFilterArtists] = useState<Artist[]>([])
  const [filterTags, setFilterTags] = useState<Tag[]>([])
  const [filtersLoading, setFiltersLoading] = useState(true)
  const [selectedArtistIds, setSelectedArtistIds] = useState<number[]>([])
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([])

  const [createOpen, setCreateOpen] = useState(false)
  const [editSong, setEditSong] = useState<Song | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Song | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const hasFilters =
    songSearch.apiQuery !== undefined ||
    selectedArtistIds.length > 0 ||
    selectedTagIds.length > 0

  const loadFilters = useCallback(async () => {
    setFiltersLoading(true)
    try {
      const [artists, tags] = await Promise.all([
        artistSearch.apiQuery
          ? listArtists({ username: artistSearch.apiQuery, size: 100 }).then((r) => r.items)
          : fetchAllPages((p, s) => listArtists({ page: p, size: s })),
        tagSearch.apiQuery
          ? listTags({ name: tagSearch.apiQuery, size: 100 }).then((r) => r.items)
          : fetchAllPages((p, s) => listTags({ page: p, size: s })),
      ])
      setFilterArtists(artists)
      setFilterTags(tags)
    } catch {
      setFilterArtists([])
      setFilterTags([])
    } finally {
      setFiltersLoading(false)
    }
  }, [artistSearch.apiQuery, tagSearch.apiQuery])

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listSongs({
        page,
        size,
        name: songSearch.apiQuery,
        artistIds: selectedArtistIds,
        tagIds: selectedTagIds,
      })
      setData(res.items)
      setPages(res.pages)
      setTotal(res.total)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors du chargement.')
    } finally {
      setLoading(false)
    }
  }, [page, size, songSearch.apiQuery, selectedArtistIds, selectedTagIds])

  useEffect(() => {
    void loadFilters()
  }, [loadFilters])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    reset()
    setPage(1)
  }, [songSearch.apiQuery, reset, setPage])

  function handleFilterArtists(ids: number[]) {
    setSelectedArtistIds(ids)
    reset()
    setPage(1)
  }

  function handleFilterTags(ids: number[]) {
    setSelectedTagIds(ids)
    reset()
    setPage(1)
  }

  function clearFilters() {
    songSearch.setValue('')
    artistSearch.setValue('')
    tagSearch.setValue('')
    setSelectedArtistIds([])
    setSelectedTagIds([])
    reset()
    setPage(1)
  }

  async function reloadAfterMutation() {
    await Promise.all([load(), loadFilters()])
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

  async function handleEdit(name: string) {
    if (!editSong) return
    setSubmitting(true)
    setError(null)
    try {
      await updateSong(editSong.id, { name })
      setEditSong(null)
      setSuccess('Chanson mise à jour.')
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors de la mise à jour.')
    } finally {
      setSubmitting(false)
    }
  }

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

  const artistFilterItems = useMemo(
    () => filterArtists.map((a) => ({ id: a.id, label: a.username })),
    [filterArtists],
  )

  const tagFilterItems = useMemo(
    () => filterTags.map((t) => ({ id: t.id, label: t.name })),
    [filterTags],
  )

  const columns = useMemo<Column<Song>[]>(
    () => [
      {
        key: 'name',
        header: 'Nom',
        render: (row) => <strong>{row.name}</strong>,
      },
      {
        key: 'file',
        header: 'Fichier',
        render: (row) =>
          row.file ? (
            <span className="muted">
              {row.file.name} · {formatBytes(row.file.size)}
            </span>
          ) : (
            <span className="muted">—</span>
          ),
      },
      {
        key: 'player',
        header: 'Écouter',
        render: (row) => <AudioPlayer fileId={row.file_id} />,
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
          <>
            <Button variant="ghost" onClick={() => setEditSong(row)}>
              Modifier
            </Button>
            <Button variant="danger" onClick={() => setDeleteTarget(row)}>
              Supprimer
            </Button>
          </>
        ),
      },
    ],
    [],
  )

  const emptyDescription = hasFilters
    ? 'Aucune chanson ne correspond aux critères de recherche.'
    : 'Commencez par importer un fichier audio.'

  return (
    <div className="songs-page">
      <PageHeader
        title="Chansons"
        description="Gérez le catalogue audio : upload, filtres par artiste/tag, renommage et suppression."
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

      <div className="songs-page__body">
        <aside className="songs-page__filters">
          <div className="songs-page__filters-header">
            <h2 className="songs-page__filters-title">Filtres</h2>
            {hasFilters ? (
              <Button variant="ghost" onClick={clearFilters}>
                Effacer
              </Button>
            ) : null}
          </div>

          <FilterCheckboxList
            title="Artistes"
            items={artistFilterItems}
            selected={selectedArtistIds}
            onChange={handleFilterArtists}
            searchValue={artistSearch.value}
            onSearchChange={artistSearch.setValue}
            loading={filtersLoading}
            searchPlaceholder="Filtrer par artiste…"
          />

          <FilterCheckboxList
            title="Tags"
            items={tagFilterItems}
            selected={selectedTagIds}
            onChange={handleFilterTags}
            searchValue={tagSearch.value}
            onSearchChange={tagSearch.setValue}
            loading={filtersLoading}
            searchPlaceholder="Filtrer par tag…"
          />
        </aside>

        <div className="songs-page__main">
          <SearchInput
            className="songs-page__search"
            value={songSearch.value}
            onChange={songSearch.setValue}
            placeholder="Rechercher une chanson…"
            aria-label="Rechercher une chanson"
          />

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
                columns={columns}
                data={data}
                keyExtractor={(r) => r.id}
                loading={loading}
              />
              <Pagination page={page} pages={pages} pageSize={size} total={total} onPageChange={setPage} />
            </>
          )}
        </div>
      </div>

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
        title="Renommer la chanson"
        onClose={() => setEditSong(null)}
      >
        {editSong ? (
          <SongForm
            initialName={editSong.name}
            requireFile={false}
            loading={submitting}
            onSubmit={(name) => void handleEdit(name)}
            onCancel={() => setEditSong(null)}
          />
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
