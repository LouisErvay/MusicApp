import { useState } from 'react'
import { Button } from './Button'
import { FileInput, Input } from './Input'

interface SongFormProps {
  initialName?: string
  requireFile?: boolean
  loading?: boolean
  submitLabel?: string
  onSubmit: (name: string, file: File | null) => void
  onCancel?: () => void
}

export function SongForm({
  initialName = '',
  requireFile = true,
  loading = false,
  submitLabel = 'Enregistrer',
  onSubmit,
  onCancel,
}: SongFormProps) {
  const [name, setName] = useState(initialName)
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

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
    onSubmit(trimmed, file)
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
      ) : null}
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
