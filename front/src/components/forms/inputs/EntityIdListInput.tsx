import { useEffect, useMemo, useState } from 'react'
import { useDebouncedValue } from '../../../hooks/useDebouncedValue'
import { resolveSearchQuery } from '../../../utils/search'
import type { EntityFilterOption } from '../../data-table/TableColumnEntityFilterHeader'
import './StringListInput.css'

interface EntityIdListInputProps {
  label: string
  selectedIds: number[]
  selectedLabels: string[]
  onChange: (ids: number[], labels: string[]) => void
  placeholder?: string
  disabled?: boolean
  fetchOptions: (search?: string) => Promise<EntityFilterOption[]>
}

export function EntityIdListInput({
  label,
  selectedIds,
  selectedLabels,
  onChange,
  placeholder = 'Rechercher puis sélectionner…',
  disabled = false,
  fetchOptions,
}: EntityIdListInputProps) {
  const [draft, setDraft] = useState('')
  const debouncedDraft = useDebouncedValue(draft, 300)
  const apiQuery = useMemo(() => resolveSearchQuery(debouncedDraft), [debouncedDraft])
  const [options, setOptions] = useState<EntityFilterOption[]>([])
  const [optionsLoading, setOptionsLoading] = useState(false)

  useEffect(() => {
    let cancelled = false
    setOptionsLoading(true)

    void fetchOptions(apiQuery)
      .then((items) => {
        if (!cancelled) setOptions(items)
      })
      .catch(() => {
        if (!cancelled) setOptions([])
      })
      .finally(() => {
        if (!cancelled) setOptionsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [fetchOptions, apiQuery])

  const selectedIdSet = useMemo(() => new Set(selectedIds), [selectedIds])

  const visibleOptions = useMemo(
    () => options.filter((option) => !selectedIdSet.has(option.id)),
    [options, selectedIdSet],
  )

  function addOption(option: EntityFilterOption) {
    if (selectedIdSet.has(option.id)) return
    onChange([...selectedIds, option.id], [...selectedLabels, option.label])
    setDraft('')
  }

  function removeAt(index: number) {
    onChange(
      selectedIds.filter((_, i) => i !== index),
      selectedLabels.filter((_, i) => i !== index),
    )
  }

  return (
    <div className="string-list">
      <span className="string-list__label">{label}</span>
      <div className="string-list__box">
        {selectedLabels.map((value, index) => (
          <span key={`${selectedIds[index]}-${value}`} className="chip">
            {value}
            <button
              type="button"
              className="string-list__remove"
              onClick={() => removeAt(index)}
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
          placeholder={selectedIds.length === 0 ? placeholder : ''}
          disabled={disabled}
          maxLength={100}
        />
      </div>
      {draft.trim().length > 0 && draft.trim().length < 3 ? (
        <span className="string-list__hint">Saisir au moins 3 caractères pour rechercher</span>
      ) : (
        <span className="string-list__hint">Cliquer sur une suggestion pour ajouter</span>
      )}
      {draft.trim().length >= 3 || apiQuery ? (
        <div className="string-list__suggestions">
          {optionsLoading ? (
            <span className="string-list__suggestion-empty">Recherche…</span>
          ) : visibleOptions.length === 0 ? (
            <span className="string-list__suggestion-empty">Aucune suggestion</span>
          ) : (
            visibleOptions.map((option) => (
              <button
                key={option.id}
                type="button"
                className="string-list__suggestion"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => addOption(option)}
                disabled={disabled}
              >
                {option.label}
              </button>
            ))
          )}
        </div>
      ) : null}
    </div>
  )
}
