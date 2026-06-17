import { useCallback, useRef } from 'react'
import { useAppShell } from './AppShellContext'
import { MIN_SIDEBAR_WIDTH } from './sidebarConstants'

export function SidebarResizeHandle() {
  const { sidebarWidth, setSidebarWidth, beginResize, endResize } = useAppShell()
  const startXRef = useRef(0)
  const startWidthRef = useRef(0)

  const onPointerDown = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      event.preventDefault()
      const handle = event.currentTarget
      handle.setPointerCapture(event.pointerId)
      startXRef.current = event.clientX
      startWidthRef.current = sidebarWidth
      beginResize()

      const onPointerMove = (moveEvent: PointerEvent) => {
        const delta = moveEvent.clientX - startXRef.current
        setSidebarWidth(startWidthRef.current + delta)
      }

      const onPointerUp = (upEvent: PointerEvent) => {
        handle.releasePointerCapture(upEvent.pointerId)
        endResize()
        document.body.style.removeProperty('cursor')
        document.body.style.removeProperty('user-select')
        window.removeEventListener('pointermove', onPointerMove)
        window.removeEventListener('pointerup', onPointerUp)
      }

      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
      window.addEventListener('pointermove', onPointerMove)
      window.addEventListener('pointerup', onPointerUp)
    },
    [beginResize, endResize, setSidebarWidth, sidebarWidth],
  )

  return (
    <div
      className="sidebar-panel__resize-handle"
      role="separator"
      aria-orientation="vertical"
      aria-valuemin={MIN_SIDEBAR_WIDTH}
      aria-valuenow={sidebarWidth}
      aria-label="Redimensionner la barre latérale"
      onPointerDown={onPointerDown}
    />
  )
}
