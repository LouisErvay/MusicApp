import { Button } from './Button'
import './Pagination.css'

interface PaginationProps {
  page: number
  pages: number
  total: number
  onPageChange: (page: number) => void
}

export function Pagination({ page, pages, total, onPageChange }: PaginationProps) {
  if (pages <= 1) return null

  return (
    <nav className="pagination" aria-label="Pagination">
      <span className="pagination__info">
        {total} élément{total > 1 ? 's' : ''} · page {page}/{pages}
      </span>
      <div className="pagination__controls">
        <Button variant="secondary" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          ← Préc.
        </Button>
        <Button variant="secondary" disabled={page >= pages} onClick={() => onPageChange(page + 1)}>
          Suiv. →
        </Button>
      </div>
    </nav>
  )
}
