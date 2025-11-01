/**
 * Main Layout Component with Navigation
 */
import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>FastAPI Demo</h2>
          <p className="user-info">
            {user?.full_name}
            {user?.is_admin && <span className="admin-badge">Admin</span>}
          </p>
        </div>

        <nav className="sidebar-nav">
          <Link to="/dashboard" className={`nav-item ${isActive('/dashboard')}`}>
            <span className="nav-icon">📊</span>
            Dashboard
          </Link>

          <Link to="/profile" className={`nav-item ${isActive('/profile')}`}>
            <span className="nav-icon">👤</span>
            Profile
          </Link>

          <Link to="/tokens" className={`nav-item ${isActive('/tokens')}`}>
            <span className="nav-icon">🔑</span>
            API Tokens
          </Link>

          <Link to="/items" className={`nav-item ${isActive('/items')}`}>
            <span className="nav-icon">📦</span>
            Items
          </Link>

          {user?.is_admin && (
            <>
              <div className="nav-divider">Admin</div>
              <Link to="/admin/users" className={`nav-item ${isActive('/admin/users')}`}>
                <span className="nav-icon">👥</span>
                Users
              </Link>
            </>
          )}

          <div className="nav-divider"></div>

          <button onClick={handleLogout} className="nav-item logout-btn">
            <span className="nav-icon">🚪</span>
            Logout
          </button>
        </nav>

        <div className="sidebar-footer">
          <p>Version 1.0.0</p>
        </div>
      </aside>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;
