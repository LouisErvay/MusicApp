import { SearchInput } from './SearchInput'
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
  searchValue: string
  onSearchChange: (value: string) => void
  loading?: boolean
  searchPlaceholder?: string
}

export function FilterCheckboxList({
  title,
  items,
  selected,
  onChange,
  searchValue,
  onSearchChange,
  loading = false,
  searchPlaceholder = 'Rechercher…',
}: FilterCheckboxListProps) {
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
      <SearchInput
        value={searchValue}
        onChange={onSearchChange}
        placeholder={searchPlaceholder}
        disabled={loading}
        aria-label={`Rechercher ${title.toLowerCase()}`}
      />
      <div className="filter-list__items">
        {loading ? (
          <p className="filter-list__empty">Chargement…</p>
        ) : items.length === 0 ? (
          <p className="filter-list__empty">Aucun résultat</p>
        ) : (
          items.map((item) => (
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
