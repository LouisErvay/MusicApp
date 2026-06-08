import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { resolveSearchQuery } from '../utils/search'
import { IconButton } from './IconButton'
import './TableColumnFilterHeader.css'

export interface EntityFilterOption {
  id: number
  label: string
}

interface TableColumnEntityFilterHeaderProps {
  title: string
  appliedIds: number[]
  appliedLabels: string[]
  onApply: (ids: number[], labels: string[]) => void
  fetchOptions: (search?: string) => Promise<EntityFilterOption[]>
}

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-4-4" strokeLinecap="round" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
      <path d="M5 12l4 4L19 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
      <path d="M6 6l12 12M18 6 6 18" strokeLinecap="round" />
    </svg>
  )
}

export function TableColumnEntityFilterHeader({
  title,
  appliedIds,
  appliedLabels,
  onApply,
  fetchOptions,
}: TableColumnEntityFilterHeaderProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState('')
  const [draftIds, setDraftIds] = useState<number[]>([])
  const [labelById, setLabelById] = useState<Record<number, string>>({})
  const [options, setOptions] = useState<EntityFilterOption[]>([])
  const [optionsLoading, setOptionsLoading] = useState(false)
  const [panelOpen, setPanelOpen] = useState(false)

  const inputRef = useRef<HTMLInputElement>(null)
  const rootRef = useRef<HTMLDivElement>(null)
  const debouncedDraft = useDebouncedValue(draft, 300)

  const appliedSummary = useMemo(
    () => (appliedLabels.length > 0 ? appliedLabels.join('; ') : undefined),
    [appliedLabels],
  )

  const loadOptions = useCallback(async () => {
    setOptionsLoading(true)
    try {
      const query = resolveSearchQuery(debouncedDraft)
      const items = await fetchOptions(query)
      setOptions(items)
      setLabelById((prev) => {
        const next = { ...prev }
        for (const item of items) next[item.id] = item.label
        return next
      })
    } catch {
      setOptions([])
    } finally {
      setOptionsLoading(false)
    }
  }, [debouncedDraft, fetchOptions])

  useEffect(() => {
    if (!editing) return
    void loadOptions()
  }, [editing, loadOptions])

  useEffect(() => {
    if (editing) inputRef.current?.focus()
  }, [editing])

  useEffect(() => {
    if (!editing) return

    function handlePointerDown(e: MouseEvent) {
      if (!rootRef.current?.contains(e.target as Node)) {
        setPanelOpen(false)
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    return () => document.removeEventListener('mousedown', handlePointerDown)
  }, [editing])

  function startEdit() {
    setDraft('')
    setDraftIds([...appliedIds])
    setLabelById(
      appliedIds.reduce<Record<number, string>>((acc, id, index) => {
        acc[id] = appliedLabels[index] ?? String(id)
        return acc
      }, {}),
    )
    setPanelOpen(false)
    setEditing(true)
  }

  function cancelEdit() {
    setDraft('')
    setDraftIds([...appliedIds])
    setPanelOpen(false)
    setEditing(false)
  }

  function applyEdit() {
    const labels = draftIds.map((id) => labelById[id] ?? String(id))
    onApply(draftIds, labels)
    setPanelOpen(false)
    setEditing(false)
  }

  function toggleOption(id: number, label: string) {
    setDraftIds((prev) => {
      if (prev.includes(id)) return prev.filter((item) => item !== id)
      return [...prev, id]
    })
    setLabelById((prev) => ({ ...prev, [id]: label }))
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') applyEdit()
    if (e.key === 'Escape') cancelEdit()
  }

  return (
    <div className="table-col-filter" ref={rootRef}>
      <div className="table-col-filter__row">
        {editing ? (
          <>
            <IconButton
              className="table-col-filter__action"
              label="Appliquer les filtres"
              variant="accent"
              onClick={applyEdit}
            >
              <CheckIcon />
            </IconButton>
            <IconButton
              className="table-col-filter__action"
              label="Annuler les filtres"
              onClick={cancelEdit}
            >
              <CloseIcon />
            </IconButton>
            <div
              className="table-col-filter__input-wrap"
              onMouseEnter={() => setPanelOpen(true)}
            >
              <input
                ref={inputRef}
                type="text"
                className="table-col-filter__input"
                value={draft}
                placeholder="recherche"
                onChange={(e) => setDraft(e.target.value)}
                onFocus={() => setPanelOpen(true)}
                onKeyDown={handleKeyDown}
                aria-label={`Filtrer par ${title.toLowerCase()}`}
                aria-expanded={panelOpen}
              />
              {panelOpen ? (
                <div className="table-col-filter__panel" role="listbox">
                  {optionsLoading ? (
                    <p className="table-col-filter__panel-empty">Chargement…</p>
                  ) : options.length === 0 ? (
                    <p className="table-col-filter__panel-empty">Aucun élément</p>
                  ) : (
                    <ul className="table-col-filter__options">
                      {options.map((option) => (
                        <li key={option.id}>
                          <label className="table-col-filter__option">
                            <input
                              type="checkbox"
                              checked={draftIds.includes(option.id)}
                              onChange={() => toggleOption(option.id, option.label)}
                            />
                            <span>{option.label}</span>
                          </label>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : null}
            </div>
          </>
        ) : (
          <>
            <IconButton
              className="table-col-filter__action"
              label={`Filtrer par ${title.toLowerCase()}`}
              onClick={startEdit}
            >
              <SearchIcon />
            </IconButton>
            <span className="table-col-filter__title">{title}</span>
            {appliedSummary ? (
              <span className="table-col-filter__active" title={appliedSummary}>
                {appliedSummary}
              </span>
            ) : null}
          </>
        )}
      </div>
    </div>
  )
}
