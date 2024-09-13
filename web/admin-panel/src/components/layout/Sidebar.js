import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Users, Truck, Settings, ChevronLeft, ChevronRight, Cog, LayoutGrid, Shield, MapPin } from 'lucide-react';

const Sidebar = ({ minimized, toggleMinimize }) => {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', icon: Home, path: '/' },
    { name: 'Users', icon: Users, path: '/users' },
    { name: 'Vehicles', icon: Truck, path: '/vehicles' },
    { name: 'GPS & Vehicles', icon: MapPin, path: '/gps-vehicle' },
    { 
      name: 'Admin', 
      icon: Cog, 
      path: '/admin',
      subItems: [
        { name: 'Menu Management', icon: LayoutGrid, path: '/admin?tab=menu' },
        { name: 'Profile Management', icon: Shield, path: '/admin?tab=profiles' },
        { name: 'System Settings', icon: Settings, path: '/admin?tab=settings' },
      ]
    },
  ];


  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between h-16 px-4 border-b dark:border-gray-700">
        {!minimized && <span className="text-2xl font-semibold text-gray-800 dark:text-white">Admin Panel</span>}
        <button onClick={toggleMinimize} className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700">
          {minimized ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto">
        {navItems.map((item) => (
          <div key={item.name}>
            <Link
              to={item.path}
              className={`
                flex items-center px-4 py-2 mt-2 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg
                ${location.pathname === item.path ? 'bg-gray-200 dark:bg-gray-700' : ''}
              `}
            >
              <item.icon className="w-6 h-6" />
              {!minimized && <span className="mx-4">{item.name}</span>}
            </Link>
            {!minimized && item.subItems && (
              <div className="ml-6 mt-2">
                {item.subItems.map((subItem) => (
                  <Link
                    key={subItem.name}
                    to={subItem.path}
                    className={`
                      flex items-center px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg
                      ${location.pathname + location.search === subItem.path ? 'bg-gray-200 dark:bg-gray-700' : ''}
                    `}
                  >
                    <subItem.icon className="w-5 h-5" />
                    <span className="mx-4">{subItem.name}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;