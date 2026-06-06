import { useCallback, useEffect, useMemo, useState } from 'react'
import { createTag, deleteTag, listTags, updateTag } from '../api/tags'
import { Alert } from '../components/Alert'
import { Button } from '../components/Button'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { DataTable } from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { EmptyState } from '../components/EmptyState'
import { Modal } from '../components/Modal'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { SearchInput } from '../components/SearchInput'
import { TagForm } from '../components/TagForm'
import { usePagination } from '../hooks/usePagination'
import { useSearchQuery } from '../hooks/useSearchQuery'
import type { Tag } from '../types'
import { ApiError } from '../types'
import { formatDate } from '../utils/format'

export function TagsPage() {
  const { page, size, setPage, reset } = usePagination()
  const search = useSearchQuery()

  const [data, setData] = useState<Tag[]>([])
  const [pages, setPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [createOpen, setCreateOpen] = useState(false)
  const [editTag, setEditTag] = useState<Tag | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Tag | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const hasSearch = search.apiQuery !== undefined

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listTags({
        page,
        size,
        name: search.apiQuery,
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

  async function handleCreate(name: string) {
    setSubmitting(true)
    setError(null)
    try {
      await createTag({ name })
      setCreateOpen(false)
      setSuccess('Tag créé.')
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
    if (!editTag) return
    setSubmitting(true)
    setError(null)
    try {
      await updateTag(editTag.id, { name })
      setEditTag(null)
      setSuccess('Tag mis à jour.')
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
      await deleteTag(deleteTarget.id)
      setDeleteTarget(null)
      setSuccess('Tag supprimé.')
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Erreur lors de la suppression.')
    } finally {
      setSubmitting(false)
    }
  }

  const columns = useMemo<Column<Tag>[]>(
    () => [
      {
        key: 'name',
        header: 'Nom',
        render: (row) => <span className="tag-badge">{row.name}</span>,
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
            <Button variant="ghost" onClick={() => setEditTag(row)}>
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
        title="Tags"
        description="Organisez votre catalogue avec des étiquettes."
        actions={<Button onClick={() => setCreateOpen(true)}>+ Ajouter un tag</Button>}
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
        placeholder="Rechercher un tag…"
        aria-label="Rechercher un tag"
      />

      {!loading && data.length === 0 ? (
        <EmptyState
          icon="◈"
          title="Aucun tag"
          description={
            hasSearch
              ? 'Aucun tag ne correspond à votre recherche.'
              : 'Créez des tags pour catégoriser vos contenus.'
          }
          action={
            hasSearch ? (
              <Button variant="secondary" onClick={() => search.setValue('')}>
                Effacer la recherche
              </Button>
            ) : (
              <Button onClick={() => setCreateOpen(true)}>Ajouter un tag</Button>
            )
          }
        />
      ) : (
        <>
          <DataTable columns={columns} data={data} keyExtractor={(r) => r.id} loading={loading} />
          <Pagination page={page} pages={pages} total={total} onPageChange={setPage} />
        </>
      )}

      <Modal open={createOpen} title="Nouveau tag" onClose={() => setCreateOpen(false)}>
        <TagForm
          loading={submitting}
          onSubmit={handleCreate}
          onCancel={() => setCreateOpen(false)}
        />
      </Modal>

      <Modal open={editTag !== null} title="Modifier le tag" onClose={() => setEditTag(null)}>
        {editTag ? (
          <TagForm
            initialName={editTag.name}
            loading={submitting}
            onSubmit={(name) => void handleEdit(name)}
            onCancel={() => setEditTag(null)}
          />
        ) : null}
      </Modal>

      <ConfirmDialog
        open={deleteTarget !== null}
        title="Supprimer le tag"
        message={`Supprimer « ${deleteTarget?.name ?? ''} » ?`}
        loading={submitting}
        onConfirm={() => void handleDelete()}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
