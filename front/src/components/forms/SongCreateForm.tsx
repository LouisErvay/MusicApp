import { useCallback, useState } from 'react'
import { listArtists } from '../../api/artists'
import { listTags } from '../../api/tags'
import { nameWithoutExtension } from '../../utils/fileName'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { StringListInput } from './inputs/StringListInput'
import './SongCreateForm.css'

export interface SongCreateEntry {
  name: string
  file: File
}

export interface SongCreatePayload {
  entries: SongCreateEntry[]
  artists: string[]
  tags: string[]
}

interface SongCreateFormProps {
  loading?: boolean
  onSubmit: (payload: SongCreatePayload) => void
  onCancel?: () => void
}

export function SongCreateForm({ loading = false, onSubmit, onCancel }: SongCreateFormProps) {
  const [entries, setEntries] = useState<SongCreateEntry[]>([])
  const [artists, setArtists] = useState<string[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  const fetchArtistSuggestions = useCallback(
    (query: string) =>
      listArtists({ username: query, size: 20 }).then((res) =>
        res.items.map((a) => a.username),
      ),
    [],
  )

  const fetchTagSuggestions = useCallback(
    (query: string) =>
      listTags({ name: query, size: 20 }).then((res) => res.items.map((t) => t.name)),
    [],
  )

  function handleFilesSelected(fileList: FileList | null) {
    if (!fileList || fileList.length === 0) return
    const files = Array.from(fileList)
    setEntries(
      files.map((file) => ({
        file,
        name: nameWithoutExtension(file.name),
      })),
    )
    setError(null)
  }

  function updateEntryName(index: number, name: string) {
    setEntries((prev) =>
      prev.map((entry, i) => (i === index ? { ...entry, name } : entry)),
    )
  }

  function removeEntry(index: number) {
    setEntries((prev) => prev.filter((_, i) => i !== index))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (entries.length === 0) {
      setError('Sélectionnez au moins un fichier audio.')
      return
    }
    const invalid = entries.find((entry) => !entry.name.trim())
    if (invalid) {
      setError('Chaque chanson doit avoir un nom.')
      return
    }
    setError(null)
    onSubmit({
      entries: entries.map((entry) => ({
        ...entry,
        name: entry.name.trim(),
      })),
      artists,
      tags,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="entity-form song-create-form">
      {error ? <p className="entity-form__error">{error}</p> : null}

      <label className="field field--file">
        <span className="field__label">Fichiers audio</span>
        <input
          type="file"
          className="field__file"
          accept="audio/*"
          multiple
          onChange={(e) => handleFilesSelected(e.target.files)}
          disabled={loading}
        />
        <span className="song-create-form__file-hint">
          Un ou plusieurs fichiers — les métadonnées communes s&apos;appliquent à tous
        </span>
      </label>

      {entries.length > 0 ? (
        <div className="song-create-form__entries">
          <span className="field__label">
            {entries.length === 1 ? 'Chanson' : `${entries.length} chansons`}
          </span>
          <ul className="song-create-form__list">
            {entries.map((entry, index) => (
              <li key={`${entry.file.name}-${index}`} className="song-create-form__row">
                <div className="song-create-form__file-meta">
                  <span className="song-create-form__filename" title={entry.file.name}>
                    {entry.file.name}
                  </span>
                  {entries.length > 1 ? (
                    <button
                      type="button"
                      className="song-create-form__remove-file"
                      onClick={() => removeEntry(index)}
                      disabled={loading}
                      aria-label="Retirer ce fichier"
                    >
                      Retirer
                    </button>
                  ) : null}
                </div>
                <Input
                  label={entries.length === 1 ? 'Nom' : `Nom #${index + 1}`}
                  value={entry.name}
                  onChange={(e) => updateEntryName(index, e.target.value)}
                  maxLength={100}
                  required
                  disabled={loading}
                />
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <StringListInput
        label="Artistes"
        values={artists}
        onChange={setArtists}
        placeholder="Ex. Daft Punk"
        disabled={loading}
        fetchSuggestions={fetchArtistSuggestions}
      />

      <StringListInput
        label="Tags"
        values={tags}
        onChange={setTags}
        placeholder="Ex. electro"
        disabled={loading}
        fetchSuggestions={fetchTagSuggestions}
      />

      <div className="entity-form__actions">
        {onCancel ? (
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Annuler
          </Button>
        ) : null}
        <Button type="submit" loading={loading}>
          {entries.length <= 1 ? 'Importer' : `Importer ${entries.length} chansons`}
        </Button>
      </div>
    </form>
  )
}
