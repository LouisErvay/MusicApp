import { useState } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'

interface TagFormProps {
  initialName?: string
  loading?: boolean
  submitLabel?: string
  onSubmit: (name: string) => void
  onCancel?: () => void
}

export function TagForm({
  initialName = '',
  loading = false,
  submitLabel = 'Enregistrer',
  onSubmit,
  onCancel,
}: TagFormProps) {
  const [name, setName] = useState(initialName)
  const [error, setError] = useState<string | null>(null)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = name.trim()
    if (!trimmed) {
      setError('Le nom est obligatoire.')
      return
    }
    setError(null)
    onSubmit(trimmed)
  }

  return (
    <form onSubmit={handleSubmit} className="entity-form">
      {error ? <p className="entity-form__error">{error}</p> : null}
      <Input
        label="Nom du tag"
        value={name}
        onChange={(e) => setName(e.target.value)}
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
