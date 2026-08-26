import { NavLink } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
  const navClass = ({ isActive }: { isActive: boolean }) =>
    `sidebar-link ${isActive ? 'active' : ''}`

  return (
    <aside className="sidebar">

      <div className="sidebar-inner">

        <div className="sidebar-section">

          <span className="sidebar-label">
            Workspace
          </span>

          <NavLink
            to="/dashboard"
            className={navClass}
          >
            <span className="sidebar-icon">⌂</span>
            <span>Dashboard</span>
          </NavLink>

        </div>

        <div className="sidebar-section">

          <span className="sidebar-label">
            AI Services
          </span>

          <NavLink
            to="/prediction"
            className={navClass}
          >
            <span className="sidebar-icon">✦</span>
            <span>Performance Prediction</span>
          </NavLink>

          <NavLink
            to="/study-plan"
            className={navClass}
          >
            <span className="sidebar-icon">◈</span>
            <span>Study Plan</span>
          </NavLink>

          <NavLink
            to="/eligibility"
            className={navClass}
          >
            <span className="sidebar-icon">✓</span>
            <span>Eligibility</span>
          </NavLink>

        </div>

        <div className="sidebar-section">

          <span className="sidebar-label">
            Academic
          </span>

          <NavLink
            to="/history"
            className={navClass}
          >
            <span className="sidebar-icon">◷</span>
            <span>Academic History</span>
          </NavLink>

        </div>

        <div className="sidebar-section">

          <span className="sidebar-label">
            Account
          </span>

          <NavLink
            to="/profile"
            className={navClass}
          >
            <span className="sidebar-icon">◯</span>
            <span>Profile</span>
          </NavLink>

          <NavLink
            to="/settings"
            className={navClass}
          >
            <span className="sidebar-icon">⚙</span>
            <span>Settings</span>
          </NavLink>

        </div>

        <div className="sidebar-bottom">

          <div className="sidebar-ai-status">
            <span className="status-indicator" />

            <div>
              <strong>AI Services</strong>
              <span>System operational</span>
            </div>
          </div>

          <button className="sidebar-logout">
            ↪
            <span>Sign out</span>
          </button>

        </div>

      </div>

    </aside>
  )
}

export default Sidebar