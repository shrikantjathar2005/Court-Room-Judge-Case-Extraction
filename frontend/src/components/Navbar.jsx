import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  HiOutlineHome,
  HiOutlineUpload,
  HiOutlineSearch,
  HiOutlineDocumentText,
  HiOutlineShieldCheck,
  HiOutlineLogout,
  HiOutlineUser,
} from 'react-icons/hi';

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', icon: HiOutlineHome, label: 'Dashboard' },
    { path: '/upload', icon: HiOutlineUpload, label: 'Upload' },
    { path: '/search', icon: HiOutlineSearch, label: 'Search' },
  ];

  if (isAdmin) {
    navItems.push({ path: '/admin', icon: HiOutlineShieldCheck, label: 'Admin' });
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-surface-700/50 rounded-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-primary-600/25 group-hover:shadow-primary-500/40 transition-shadow">
              <HiOutlineDocumentText className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                DocDigitizer
              </span>
              <span className="hidden sm:block text-[10px] text-gray-500 -mt-1 font-hindi">
                दस्तावेज़ डिजिटाइज़र
              </span>
            </div>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-1">
            {navItems.map(({ path, icon: Icon, label }) => {
              const isActive = location.pathname === path;
              return (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-surface-700/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{label}</span>
                </Link>
              );
            })}
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-surface-800/50 border border-surface-700">
              <HiOutlineUser className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-300">{user?.full_name || user?.email}</span>
              <span className={`badge ${
                user?.role === 'admin' ? 'badge-error' : 
                user?.role === 'reviewer' ? 'badge-warning' : 'badge-info'
              }`}>
                {user?.role}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all duration-200"
              title="Logout"
            >
              <HiOutlineLogout className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
