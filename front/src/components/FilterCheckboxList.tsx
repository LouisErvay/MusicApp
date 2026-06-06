import { useMemo, useState } from 'react'
import './FilterCheckboxList.css'

export interface FilterItem {
  id: number
  label: string
}

interface FilterCheckboxListProps {
  title: string
  items: FilterItem[]
  selected: number[]
  onChange: (selected: number[]) => void
  loading?: boolean
}

export function FilterCheckboxList({
  title,
  items,
  selected,
  onChange,
  loading = false,
}: FilterCheckboxListProps) {
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return items
    return items.filter((item) => item.label.toLowerCase().includes(q))
  }, [items, search])

  function toggle(id: number) {
    if (selected.includes(id)) {
      onChange(selected.filter((s) => s !== id))
    } else {
      onChange([...selected, id])
    }
  }

  return (
    <section className="filter-list">
      <h3 className="filter-list__title">{title}</h3>
      <input
        type="search"
        className="filter-list__search"
        placeholder="Rechercher…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        disabled={loading}
      />
      <div className="filter-list__items">
        {loading ? (
          <p className="filter-list__empty">Chargement…</p>
        ) : filtered.length === 0 ? (
          <p className="filter-list__empty">
            {items.length === 0 ? 'Aucun élément' : 'Aucun résultat'}
          </p>
        ) : (
          filtered.map((item) => (
            <label key={item.id} className="filter-list__item">
              <input
                type="checkbox"
                checked={selected.includes(item.id)}
                onChange={() => toggle(item.id)}
              />
              <span>{item.label}</span>
            </label>
          ))
        )}
      </div>
    </section>
  )
}
