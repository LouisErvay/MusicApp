import { useLayoutEffect, useRef, type CSSProperties, type ReactNode } from 'react'
import { AppShellProvider, useAppShell } from './AppShellContext'
import { SidebarResizeHandle } from './SidebarResizeHandle'
import { SidebarToggle } from './SidebarToggle'
import { useToggleContentInset } from './useToggleContentInset'
import './AppShell.css'

type AppShellProps = {
  sidebar: ReactNode
  children: ReactNode
}

function AppShellFrame({ sidebar, children }: AppShellProps) {
  const { isSidebarOpen, sidebarWidth, isResizing } = useAppShell()
  const shellRef = useRef<HTMLDivElement>(null)
  const toggleRef = useRef<HTMLButtonElement>(null)
  const contentRef = useRef<HTMLElement>(null)

  useLayoutEffect(() => {
    const shell = shellRef.current
    const toggle = toggleRef.current
    if (!shell || !toggle) return

    const paddingInline =
      getComputedStyle(shell)
        .getPropertyValue('--app-shell-content-padding-inline')
        .trim() || '2rem'

    if (isSidebarOpen) {
      const halfToggle = toggle.offsetWidth / 2
      toggle.style.left = `${Math.max(sidebarWidth - halfToggle, 0)}px`
    } else {
      toggle.style.left = paddingInline
    }
  }, [isSidebarOpen, sidebarWidth])

  useToggleContentInset(shellRef, toggleRef, contentRef, [
    isSidebarOpen,
    sidebarWidth,
    isResizing,
  ])

  return (
    <div
      ref={shellRef}
      className={`app-shell ${isResizing ? 'app-shell--resizing' : ''} ${
        isSidebarOpen ? '' : 'app-shell--sidebar-collapsed'
      }`}
      style={{ '--app-sidebar-width': `${sidebarWidth}px` } as CSSProperties}
    >
      <div
        className="sidebar-panel"
        style={{ width: sidebarWidth }}
        aria-hidden={!isSidebarOpen}
      >
        {sidebar}
        {isSidebarOpen ? <SidebarResizeHandle /> : null}
      </div>

      <SidebarToggle ref={toggleRef} />

      <main ref={contentRef} className="app-shell__content">
        {children}
      </main>
    </div>
  )
}

export function AppShell({ sidebar, children }: AppShellProps) {
  return (
    <AppShellProvider>
      <AppShellFrame sidebar={sidebar}>{children}</AppShellFrame>
    </AppShellProvider>
  )
}
