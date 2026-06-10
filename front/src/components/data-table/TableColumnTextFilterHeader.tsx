import { useEffect, useRef, useState } from 'react'
import { IconButton } from '../ui/IconButton'
import './TableColumnFilterHeader.css'

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

interface TableColumnTextFilterHeaderProps {
  title: string
  appliedLabel?: string
  onApply: (value: string) => void
}

export function TableColumnTextFilterHeader({
  title,
  appliedLabel,
  onApply,
}: TableColumnTextFilterHeaderProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (editing) inputRef.current?.focus()
  }, [editing])

  function startEdit() {
    setDraft(appliedLabel ?? '')
    setEditing(true)
  }

  function cancelEdit() {
    setDraft(appliedLabel ?? '')
    setEditing(false)
  }

  function applyEdit() {
    onApply(draft)
    setEditing(false)
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') applyEdit()
    if (e.key === 'Escape') cancelEdit()
  }

  return (
    <div className="table-col-filter">
      <div className="table-col-filter__row">
        {editing ? (
          <>
            <IconButton
              className="table-col-filter__action"
              label="Appliquer la recherche"
              variant="accent"
              onClick={applyEdit}
            >
              <CheckIcon />
            </IconButton>
            <IconButton
              className="table-col-filter__action"
              label="Annuler la recherche"
              onClick={cancelEdit}
            >
              <CloseIcon />
            </IconButton>
            <input
              ref={inputRef}
              type="text"
              className="table-col-filter__input"
              value={draft}
              placeholder="recherche"
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={handleKeyDown}
              aria-label={`Rechercher par ${title.toLowerCase()}`}
            />
          </>
        ) : (
          <>
            <IconButton
              className="table-col-filter__action"
              label={`Rechercher par ${title.toLowerCase()}`}
              onClick={startEdit}
            >
              <SearchIcon />
            </IconButton>
            <span className="table-col-filter__title">{title}</span>
            {appliedLabel ? (
              <span className="table-col-filter__active" title={appliedLabel}>
                {appliedLabel}
              </span>
            ) : null}
          </>
        )}
      </div>
    </div>
  )
}
