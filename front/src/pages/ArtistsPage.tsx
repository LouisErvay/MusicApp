import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  createArtist,
  deleteArtist,
  listArtists,
  updateArtist,
} from '../api/artists'
import { Alert } from '../components/Alert'
import { ArtistForm } from '../components/ArtistForm'
import { Button } from '../components/Button'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { DataTable } from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { EmptyState } from '../components/EmptyState'
import { Modal } from '../components/Modal'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { SearchInput } from '../components/SearchInput'
import { usePagination } from '../hooks/usePagination'
import { useSearchQuery } from '../hooks/useSearchQuery'
import type { Artist } from '../types'
import { ApiError } from '../types'
import { formatDate } from '../utils/format'

export function ArtistsPage() {
  const { page, size, setPage, reset } = usePagination()
  const search = useSearchQuery()

  const [data, setData] = useState<Artist[]>([])
  const [pages, setPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [createOpen, setCreateOpen] = useState(false)
  const [editArtist, setEditArtist] = useState<Artist | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Artist | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const hasSearch = search.apiQuery !== undefined

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listArtists({
        page,
        size,
        username: search.apiQuery,
      })
      setData(res.items)
      setPages(res.pages)
      setTotal(res.total)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors du chargement.')
    } finally {
      setLoading(false)
    }
  }, [page, size, search.apiQuery])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    reset()
    setPage(1)
  }, [search.apiQuery, reset, setPage])

  async function handleCreate(username: string) {
    setSubmitting(true)
    setError(null)
    try {
      await createArtist({ username })
      setCreateOpen(false)
      setSuccess('Artiste créé.')
      reset()
      setPage(1)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors de la création.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleEdit(username: string) {
    if (!editArtist) return
    setSubmitting(true)
    setError(null)
    try {
      await updateArtist(editArtist.id, { username })
      setEditArtist(null)
      setSuccess('Artiste mis à jour.')
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
      await deleteArtist(deleteTarget.id)
      setDeleteTarget(null)
      setSuccess('Artiste supprimé.')
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors de la suppression.')
    } finally {
      setSubmitting(false)
    }
  }

  const columns = useMemo<Column<Artist>[]>(
    () => [
      {
        key: 'username',
        header: "Nom d'utilisateur",
        render: (row) => <strong>{row.username}</strong>,
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
            <Button variant="ghost" onClick={() => setEditArtist(row)}>
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

  return (
    <div>
      <PageHeader
        title="Artistes"
        description="Créez et gérez les profils artistes."
        actions={<Button onClick={() => setCreateOpen(true)}>+ Ajouter un artiste</Button>}
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

      <SearchInput
        className="list-toolbar__search"
        value={search.value}
        onChange={search.setValue}
        placeholder="Rechercher un artiste…"
        aria-label="Rechercher un artiste"
      />

      {!loading && data.length === 0 ? (
        <EmptyState
          icon="◎"
          title="Aucun artiste"
          description={
            hasSearch
              ? 'Aucun artiste ne correspond à votre recherche.'
              : 'Ajoutez votre premier artiste au catalogue.'
          }
          action={
            hasSearch ? (
              <Button variant="secondary" onClick={() => search.setValue('')}>
                Effacer la recherche
              </Button>
            ) : (
              <Button onClick={() => setCreateOpen(true)}>Ajouter un artiste</Button>
            )
          }
        />
      ) : (
        <>
          <DataTable columns={columns} data={data} keyExtractor={(r) => r.id} loading={loading} />
          <Pagination page={page} pages={pages} total={total} onPageChange={setPage} />
        </>
      )}

      <Modal open={createOpen} title="Nouvel artiste" onClose={() => setCreateOpen(false)}>
        <ArtistForm
          loading={submitting}
          onSubmit={handleCreate}
          onCancel={() => setCreateOpen(false)}
        />
      </Modal>

      <Modal
        open={editArtist !== null}
        title="Modifier l'artiste"
        onClose={() => setEditArtist(null)}
      >
        {editArtist ? (
          <ArtistForm
            initialUsername={editArtist.username}
            loading={submitting}
            onSubmit={(username) => void handleEdit(username)}
            onCancel={() => setEditArtist(null)}
          />
        ) : null}
      </Modal>

      <ConfirmDialog
        open={deleteTarget !== null}
        title="Supprimer l'artiste"
        message={`Supprimer « ${deleteTarget?.username ?? ''} » ?`}
        loading={submitting}
        onConfirm={() => void handleDelete()}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
