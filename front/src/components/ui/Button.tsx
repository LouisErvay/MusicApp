import type { ReactNode } from 'react'
import './Button.css'

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  loading?: boolean
  children: ReactNode
}

export function Button({
  variant = 'primary',
  loading = false,
  disabled,
  className = '',
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      type="button"
      className={`btn btn--${variant} ${className}`.trim()}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <span className="btn__spinner" aria-hidden /> : null}
      {children}
    </button>
  )
}
