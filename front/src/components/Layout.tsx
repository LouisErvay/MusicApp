import { NavLink, Outlet } from 'react-router-dom'
import './Layout.css'

const NAV = [
  { to: '/', label: 'Tableau de bord', icon: '◉' },
  { to: '/songs', label: 'Chansons', icon: '♫' },
  { to: '/artists', label: 'Artistes', icon: '◎' },
  { to: '/tags', label: 'Tags', icon: '◈' },
]

export function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <span className="sidebar__logo" aria-hidden>
            ♪
          </span>
          <div>
            <strong>MusicApp</strong>
            <span className="sidebar__subtitle">Backoffice</span>
          </div>
        </div>
        <nav className="sidebar__nav">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`
              }
            >
              <span className="sidebar__icon" aria-hidden>
                {item.icon}
              </span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="layout__main">
        <Outlet />
      </main>
    </div>
  )
}
