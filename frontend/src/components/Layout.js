import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWebSocket } from '../context/WebSocketContext';
import { 
  Shield, LayoutDashboard, AlertTriangle, Car, Search, 
  PlusCircle, LogOut, Wifi, WifiOff, Menu, X
} from 'lucide-react';

const Layout = () => {
  const { user, logout } = useAuth();
  const { connected } = useWebSocket();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/incidents', label: 'Incidents', icon: AlertTriangle },
    { path: '/vehicles', label: 'Vehicles', icon: Car },
    { path: '/search', label: 'Search', icon: Search },
    { path: '/vehicles/add', label: 'Add Vehicle', icon: PlusCircle },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-primary-600 text-white 
        transform transition-transform duration-200 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <Shield className="w-8 h-8" />
            <div>
              <h1 className="text-xl font-bold">VNPR</h1>
              <p className="text-xs text-primary-100">Traffic Enforcement</p>
            </div>
          </div>

          <div className="mb-6 pb-6 border-b border-primary-500">
            <p className="text-sm text-primary-100">Logged in as</p>
            <p className="font-semibold">{user?.username}</p>
            <div className="flex items-center gap-2 mt-2">
              {connected ? (
                <span className="flex items-center gap-1 text-xs text-green-300">
                  <Wifi className="w-3 h-3" /> Live
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs text-red-300">
                  <WifiOff className="w-3 h-3" /> Offline
                </span>
              )}
            </div>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-white/20 text-white' 
                      : 'text-primary-100 hover:bg-white/10 hover:text-white'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <button
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 text-primary-100 hover:text-white 
                       hover:bg-white/10 rounded-lg transition-colors mt-8 w-full"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4 text-center text-xs text-primary-200">
          © 2024 VNPR System
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <header className="lg:hidden bg-white border-b px-4 py-3 flex items-center justify-between">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu className="w-6 h-6 text-gray-700" />
          </button>
          <span className="font-semibold text-gray-800">VNPR</span>
          <div className="w-6" />
        </header>

        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
