import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  DEFAULT_SIDEBAR_WIDTH,
  MAX_SIDEBAR_WIDTH,
  MIN_SIDEBAR_WIDTH,
  SIDEBAR_STORAGE_KEY,
} from './sidebarConstants'

type StoredSidebarState = {
  open: boolean
  width: number
}

type AppShellContextValue = {
  isSidebarOpen: boolean
  sidebarWidth: number
  isResizing: boolean
  openSidebar: () => void
  closeSidebar: () => void
  toggleSidebar: () => void
  setSidebarWidth: (width: number) => void
  beginResize: () => void
  endResize: () => void
}

const AppShellContext = createContext<AppShellContextValue | null>(null)

function clampSidebarWidth(width: number) {
  return Math.min(MAX_SIDEBAR_WIDTH, Math.max(MIN_SIDEBAR_WIDTH, width))
}

function readStoredSidebarState(): StoredSidebarState {
  try {
    const raw = localStorage.getItem(SIDEBAR_STORAGE_KEY)
    if (!raw) {
      return { open: true, width: DEFAULT_SIDEBAR_WIDTH }
    }
    const parsed = JSON.parse(raw) as Partial<StoredSidebarState>
    return {
      open: parsed.open ?? true,
      width: clampSidebarWidth(parsed.width ?? DEFAULT_SIDEBAR_WIDTH),
    }
  } catch {
    return { open: true, width: DEFAULT_SIDEBAR_WIDTH }
  }
}

function writeStoredSidebarState(state: StoredSidebarState) {
  localStorage.setItem(SIDEBAR_STORAGE_KEY, JSON.stringify(state))
}

export function AppShellProvider({ children }: { children: ReactNode }) {
  const stored = readStoredSidebarState()
  const [savedSidebarWidth, setSavedSidebarWidth] = useState(stored.width)
  const [isSidebarOpen, setIsSidebarOpen] = useState(stored.open)
  const [isResizing, setIsResizing] = useState(false)

  const sidebarWidth = isSidebarOpen ? savedSidebarWidth : 0

  const persist = useCallback((open: boolean, width: number) => {
    writeStoredSidebarState({ open, width: clampSidebarWidth(width) })
  }, [])

  const setSidebarWidth = useCallback(
    (width: number) => {
      const nextWidth = clampSidebarWidth(width)
      setSavedSidebarWidth(nextWidth)
      if (isSidebarOpen) {
        persist(true, nextWidth)
      }
    },
    [isSidebarOpen, persist],
  )

  const openSidebar = useCallback(() => {
    setIsSidebarOpen(true)
    persist(true, savedSidebarWidth)
  }, [persist, savedSidebarWidth])

  const closeSidebar = useCallback(() => {
    setIsSidebarOpen(false)
    persist(false, savedSidebarWidth)
  }, [persist, savedSidebarWidth])

  const toggleSidebar = useCallback(() => {
    if (isSidebarOpen) {
      closeSidebar()
    } else {
      openSidebar()
    }
  }, [closeSidebar, isSidebarOpen, openSidebar])

  const beginResize = useCallback(() => setIsResizing(true), [])
  const endResize = useCallback(() => setIsResizing(false), [])

  const value = useMemo(
    () => ({
      isSidebarOpen,
      sidebarWidth,
      isResizing,
      openSidebar,
      closeSidebar,
      toggleSidebar,
      setSidebarWidth,
      beginResize,
      endResize,
    }),
    [
      isSidebarOpen,
      sidebarWidth,
      isResizing,
      openSidebar,
      closeSidebar,
      toggleSidebar,
      setSidebarWidth,
      beginResize,
      endResize,
    ],
  )

  return (
    <AppShellContext.Provider value={value}>{children}</AppShellContext.Provider>
  )
}

export function useAppShell() {
  const context = useContext(AppShellContext)
  if (!context) {
    throw new Error('useAppShell must be used within AppShellProvider')
  }
  return context
}
