import { Outlet } from 'react-router-dom'
import { AppShell } from './AppShell'
import { Sidebar } from './Sidebar'

export function Layout() {
  return (
    <AppShell sidebar={<Sidebar />}>
      <Outlet />
    </AppShell>
  )
}
