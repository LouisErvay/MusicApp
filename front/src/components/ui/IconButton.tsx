import type { ReactNode } from 'react'
import './IconButton.css'

type IconButtonVariant = 'ghost' | 'danger' | 'accent'

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  label: string
  variant?: IconButtonVariant
  children: ReactNode
}

export function IconButton({
  label,
  variant = 'ghost',
  className = '',
  children,
  ...props
}: IconButtonProps) {
  return (
    <button
      type="button"
      className={`icon-btn icon-btn--${variant} ${className}`.trim()}
      title={label}
      aria-label={label}
      {...props}
    >
      {children}
    </button>
  )
}
