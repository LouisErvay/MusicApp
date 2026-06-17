import { NavLink } from 'react-router-dom'
import { SidebarPlayer } from './SidebarPlayer'
import './Sidebar.css'

const NAV = [
  { to: '/', label: 'Tableau de bord', icon: '◉' },
  { to: '/songs', label: 'Chansons', icon: '♫' },
  { to: '/artists', label: 'Artistes', icon: '◎' },
  { to: '/tags', label: 'Tags', icon: '◈' },
]

export function Sidebar() {
  return (
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
      <div className="sidebar__player">
        <SidebarPlayer />
      </div>
    </aside>
  )
}
