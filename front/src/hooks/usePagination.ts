import { useCallback, useState } from 'react'

export function usePagination(initialSize = 20) {
  const [page, setPage] = useState(1)
  const [size] = useState(initialSize)

  const reset = useCallback(() => setPage(1), [])

  return { page, size, setPage, reset }
}
