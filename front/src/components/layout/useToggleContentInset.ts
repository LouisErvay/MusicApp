import { useLayoutEffect, type RefObject } from 'react'

const TOGGLE_CONTENT_GAP_PX = 8

export function useToggleContentInset(
  shellRef: RefObject<HTMLElement | null>,
  toggleRef: RefObject<HTMLElement | null>,
  contentRef: RefObject<HTMLElement | null>,
  deps: unknown[],
) {
  useLayoutEffect(() => {
    const shell = shellRef.current
    const toggle = toggleRef.current
    const content = contentRef.current
    if (!shell || !toggle || !content) return

    const updateInset = () => {
      const toggleRect = toggle.getBoundingClientRect()
      const contentRect = content.getBoundingClientRect()
      const contentStyles = getComputedStyle(content)
      const paddingLeft = Number.parseFloat(contentStyles.paddingLeft) || 0
      const overlap = toggleRect.right - contentRect.left - paddingLeft

      shell.style.setProperty(
        '--app-shell-content-toggle-inset',
        overlap > 0 ? `${overlap + TOGGLE_CONTENT_GAP_PX}px` : '0px',
      )
    }

    updateInset()

    const resizeObserver = new ResizeObserver(updateInset)
    resizeObserver.observe(toggle)
    resizeObserver.observe(content)

    window.addEventListener('resize', updateInset)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', updateInset)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
}
