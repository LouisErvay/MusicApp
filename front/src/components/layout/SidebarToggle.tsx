import { forwardRef } from 'react'
import { useAppShell } from './AppShellContext'
import './SidebarToggle.css'

export const SidebarToggle = forwardRef<HTMLButtonElement>(function SidebarToggle(
  _props,
  ref,
) {
  const { isSidebarOpen, toggleSidebar } = useAppShell()

  return (
    <button
      ref={ref}
      type="button"
      className="sidebar-toggle"
      onClick={toggleSidebar}
      aria-expanded={isSidebarOpen}
      aria-label={
        isSidebarOpen ? 'Fermer la barre latérale' : 'Ouvrir la barre latérale'
      }
    >
      <span className="sidebar-toggle__icon" aria-hidden>
        {isSidebarOpen ? '‹' : '›'}
      </span>
    </button>
  )
})
