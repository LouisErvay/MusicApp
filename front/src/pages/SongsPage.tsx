import { useCallback, useEffect, useMemo, useState } from 'react'
import { createSong, deleteSong, listSongs, updateSong } from '../api/songs'
import { Alert } from '../components/Alert'
import { AudioPlayer } from '../components/AudioPlayer'
import { Button } from '../components/Button'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { DataTable } from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { EmptyState } from '../components/EmptyState'
import { Modal } from '../components/Modal'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { SongForm } from '../components/SongForm'
import { usePagination } from '../hooks/usePagination'
import type { Song } from '../types'
import { ApiError } from '../types'
import { formatBytes, formatDate } from '../utils/format'

export function SongsPage() {
  const { page, size, setPage, reset } = usePagination()
  const [data, setData] = useState<Song[]>([])
  const [pages, setPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [createOpen, setCreateOpen] = useState(false)
  const [editSong, setEditSong] = useState<Song | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Song | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listSongs(page, size)
      setData(res.items)
      setPages(res.pages)
      setTotal(res.total)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors du chargement.')
    } finally {
      setLoading(false)
    }
  }, [page, size])

  useEffect(() => {
    void load()
  }, [load])

  async function handleCreate(name: string, file: File | null) {
    if (!file) return
    setSubmitting(true)
    setError(null)
    try {
      await createSong(name, file)
      setCreateOpen(false)
      setSuccess('Chanson ajoutée.')
      reset()
      setPage(1)
      await load()
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

  return (
    <div>
      <PageHeader
        title="Chansons"
        description="Gérez le catalogue audio : upload, renommage et suppression."
        actions={
          <Button onClick={() => setCreateOpen(true)}>+ Ajouter une chanson</Button>
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
          description="Commencez par importer un fichier audio."
          action={<Button onClick={() => setCreateOpen(true)}>Ajouter une chanson</Button>}
        />
      ) : (
        <>
          <DataTable columns={columns} data={data} keyExtractor={(r) => r.id} loading={loading} />
          <Pagination page={page} pages={pages} total={total} onPageChange={setPage} />
        </>
      )}

      <Modal open={createOpen} title="Nouvelle chanson" onClose={() => setCreateOpen(false)}>
        <SongForm
          loading={submitting}
          submitLabel="Importer"
          onSubmit={handleCreate}
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
