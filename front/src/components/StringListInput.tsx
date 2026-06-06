import { useState } from 'react'
import './StringListInput.css'

interface StringListInputProps {
  label: string
  values: string[]
  onChange: (values: string[]) => void
  placeholder?: string
  disabled?: boolean
}

function normalize(value: string): string {
  return value.trim()
}

export function StringListInput({
  label,
  values,
  onChange,
  placeholder = 'Saisir puis Entrée…',
  disabled = false,
}: StringListInputProps) {
  const [draft, setDraft] = useState('')

  function addValue(raw: string) {
    const trimmed = normalize(raw)
    if (!trimmed) return
    const lower = trimmed.toLowerCase()
    if (values.some((v) => v.toLowerCase() === lower)) {
      setDraft('')
      return
    }
    onChange([...values, trimmed])
    setDraft('')
  }

  function removeValue(index: number) {
    onChange(values.filter((_, i) => i !== index))
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault()
      addValue(draft)
    }
  }

  return (
    <div className="string-list">
      <span className="string-list__label">{label}</span>
      <div className="string-list__box">
        {values.map((value, index) => (
          <span key={`${value}-${index}`} className="string-list__chip">
            {value}
            <button
              type="button"
              className="string-list__remove"
              onClick={() => removeValue(index)}
              disabled={disabled}
              aria-label={`Retirer ${value}`}
            >
              ×
            </button>
          </span>
        ))}
        <input
          type="text"
          className="string-list__input"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => addValue(draft)}
          placeholder={values.length === 0 ? placeholder : ''}
          disabled={disabled}
          maxLength={100}
        />
      </div>
      <span className="string-list__hint">Entrée pour ajouter · créés automatiquement s&apos;ils n&apos;existent pas</span>
    </div>
  )
}
