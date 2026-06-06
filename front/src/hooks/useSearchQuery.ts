import { useMemo, useState } from 'react'
import { resolveSearchQuery } from '../utils/search'
import { useDebouncedValue } from './useDebouncedValue'

const DEFAULT_DEBOUNCE_MS = 300

export function useSearchQuery(debounceMs = DEFAULT_DEBOUNCE_MS) {
  const [value, setValue] = useState('')
  const debounced = useDebouncedValue(value, debounceMs)
  const apiQuery = useMemo(() => resolveSearchQuery(debounced), [debounced])

  return {
    value,
    setValue,
    debounced,
    apiQuery,
    debouncing: value !== debounced,
  }
}
