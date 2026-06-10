import { useCallback, useEffect, useState } from 'react'
import { listArtists } from '../../api/artists'
import { listTags } from '../../api/tags'
import { Button } from '../ui/Button'
import { FileInput, Input } from '../ui/Input'
import { StringListInput } from '../StringListInput'

export interface SongFormSubmitPayload {
  name: string
  file: File | null
  artists?: string[]
  tags?: string[]
}

interface SongFormProps {
  initialName?: string
  initialArtists?: string[]
  initialTags?: string[]
  requireFile?: boolean
  loading?: boolean
  submitLabel?: string
  onSubmit: (payload: SongFormSubmitPayload) => void
  onCancel?: () => void
}

function arraysEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false
  return a.every((value, index) => value === b[index])
}

export function SongForm({
  initialName = '',
  initialArtists = [],
  initialTags = [],
  requireFile = true,
  loading = false,
  submitLabel = 'Enregistrer',
  onSubmit,
  onCancel,
}: SongFormProps) {
  const [name, setName] = useState(initialName)
  const [artists, setArtists] = useState(initialArtists)
  const [tags, setTags] = useState(initialTags)
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setName(initialName)
    setArtists(initialArtists)
    setTags(initialTags)
    setFile(null)
    setError(null)
  }, [initialName, initialArtists, initialTags])

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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = name.trim()
    if (!trimmed) {
      setError('Le nom est obligatoire.')
      return
    }
    if (requireFile && !file) {
      setError('Sélectionnez un fichier audio.')
      return
    }
    setError(null)

    const payload: SongFormSubmitPayload = { name: trimmed, file }
    if (!requireFile) {
      if (!arraysEqual(artists, initialArtists)) payload.artists = artists
      if (!arraysEqual(tags, initialTags)) payload.tags = tags
    }

    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="entity-form">
      {error ? <p className="entity-form__error">{error}</p> : null}
      <Input
        label="Nom de la chanson"
        value={name}
        onChange={(e) => setName(e.target.value)}
        maxLength={100}
        required
        autoFocus
      />
      {requireFile ? (
        <FileInput
          label="Fichier audio"
          accept="audio/*"
          onFileChange={setFile}
        />
      ) : (
        <>
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
        </>
      )}
      <div className="entity-form__actions">
        {onCancel ? (
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Annuler
          </Button>
        ) : null}
        <Button type="submit" loading={loading}>
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}
