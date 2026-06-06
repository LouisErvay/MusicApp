import { useState } from 'react'
import { Button } from './Button'
import { Input } from './Input'

interface ArtistFormProps {
  initialUsername?: string
  loading?: boolean
  submitLabel?: string
  onSubmit: (username: string) => void
  onCancel?: () => void
}

export function ArtistForm({
  initialUsername = '',
  loading = false,
  submitLabel = 'Enregistrer',
  onSubmit,
  onCancel,
}: ArtistFormProps) {
  const [username, setUsername] = useState(initialUsername)
  const [error, setError] = useState<string | null>(null)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = username.trim()
    if (!trimmed) {
      setError("Le nom d'utilisateur est obligatoire.")
      return
    }
    setError(null)
    onSubmit(trimmed)
  }

  return (
    <form onSubmit={handleSubmit} className="entity-form">
      {error ? <p className="entity-form__error">{error}</p> : null}
      <Input
        label="Nom d'utilisateur"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        maxLength={100}
        required
        autoFocus
      />
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
