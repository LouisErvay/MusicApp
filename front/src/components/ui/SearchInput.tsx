import { searchHint } from '../../utils/search'
import './SearchInput.css'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
  showHint?: boolean
  'aria-label'?: string
}

export function SearchInput({
  value,
  onChange,
  placeholder = 'Rechercher…',
  disabled = false,
  className = '',
  showHint = true,
  'aria-label': ariaLabel,
}: SearchInputProps) {
  const hint = showHint ? searchHint(value) : null

  return (
    <div className={`search-input ${className}`.trim()}>
      <input
        type="search"
        className="search-input__field"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        aria-label={ariaLabel ?? placeholder}
      />
      {hint ? <span className="search-input__hint">{hint}</span> : null}
    </div>
  )
}
