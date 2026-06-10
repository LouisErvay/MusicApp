import type { ReactNode } from 'react'
import './Alert.css'

type AlertVariant = 'error' | 'success' | 'info'

interface AlertProps {
  variant?: AlertVariant
  children: ReactNode
  onDismiss?: () => void
}

export function Alert({ variant = 'info', children, onDismiss }: AlertProps) {
  return (
    <div className={`alert alert--${variant}`} role="alert">
      <span className="alert__content">{children}</span>
      {onDismiss ? (
        <button type="button" className="alert__dismiss" onClick={onDismiss} aria-label="Fermer">
          ✕
        </button>
      ) : null}
    </div>
  )
}
