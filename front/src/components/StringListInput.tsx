import { useEffect, useMemo, useState } from 'react'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { resolveSearchQuery } from '../utils/search'
import { SearchInput } from './SearchInput'
import './StringListInput.css'

interface StringListInputProps {
  label: string
  values: string[]
  onChange: (values: string[]) => void
  placeholder?: string
  disabled?: boolean
  /** Recherche API déclenchée à partir de 3 caractères (debounce 300 ms). */
  fetchSuggestions?: (query: string) => Promise<string[]>
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
  fetchSuggestions,
}: StringListInputProps) {
  const [draft, setDraft] = useState('')
  const debouncedDraft = useDebouncedValue(draft, 300)
  const apiQuery = useMemo(() => resolveSearchQuery(debouncedDraft), [debouncedDraft])
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [suggestionsLoading, setSuggestionsLoading] = useState(false)

  useEffect(() => {
    if (!fetchSuggestions || !apiQuery) {
      setSuggestions([])
      return
    }

    let cancelled = false
    setSuggestionsLoading(true)

    void fetchSuggestions(apiQuery)
      .then((items) => {
        if (!cancelled) setSuggestions(items)
      })
      .catch(() => {
        if (!cancelled) setSuggestions([])
      })
      .finally(() => {
        if (!cancelled) setSuggestionsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [fetchSuggestions, apiQuery])

  const visibleSuggestions = useMemo(() => {
    const selected = new Set(values.map((v) => v.toLowerCase()))
    return suggestions.filter((s) => !selected.has(s.toLowerCase()))
  }, [suggestions, values])

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
    setSuggestions([])
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
      {fetchSuggestions && draft.trim().length > 0 && draft.trim().length < 3 ? (
        <span className="string-list__hint">Saisir au moins 3 caractères pour rechercher</span>
      ) : (
        <span className="string-list__hint">
          Entrée pour ajouter · créés automatiquement s&apos;ils n&apos;existent pas
        </span>
      )}
      {fetchSuggestions && apiQuery ? (
        <div className="string-list__suggestions">
          {suggestionsLoading ? (
            <span className="string-list__suggestion-empty">Recherche…</span>
          ) : visibleSuggestions.length === 0 ? (
            <span className="string-list__suggestion-empty">Aucune suggestion</span>
          ) : (
            visibleSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                className="string-list__suggestion"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => addValue(suggestion)}
                disabled={disabled}
              >
                {suggestion}
              </button>
            ))
          )}
        </div>
      ) : null}
    </div>
  )
}
