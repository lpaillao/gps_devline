import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Home, Users, Truck, Settings, ChevronLeft, ChevronRight, Cog, LayoutGrid, Shield, MapPin, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import config from '../../config/config';
const Sidebar = ({ minimized, toggleMinimize }) => {
  const [menuItems, setMenuItems] = useState([]);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  const location = useLocation();

  useEffect(() => {
    const fetchMenuItems = async () => {
      if (user && user.role_id) {
        try {
          const response = await axios.get(`${config.api.baseURL}/api/menus/role/${user.role_id}`, {
            withCredentials: true,
            headers: {
              'Content-Type': 'application/json'
            }
          });
          if (response.data.success) {
            setMenuItems(response.data.menus);
            setError(null);
          } else {
            setError('Error al obtener elementos del menú: ' + response.data.message);
          }
        } catch (error) {
          setError('Error al obtener elementos del menú: ' + error.message);
        }
      }
    };

    fetchMenuItems();
  }, [user]);

  const getIcon = (iconName) => {
    const icons = {
      Home, Users, Truck, Settings, Cog, LayoutGrid, Shield, MapPin
    };
    return icons[iconName] || Home;
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-dark-blue-800">
      <div className="flex items-center justify-between h-16 px-4 border-b dark:border-dark-blue-700">
        {!minimized && <span className="text-2xl font-semibold text-neutral-800 dark:text-neutral-100">Panel de Administración</span>}
        <button onClick={toggleMinimize} className="p-1 rounded-full hover:bg-neutral-200 dark:hover:bg-dark-blue-700">
          {minimized ? <ChevronRight size={20} className="text-neutral-600 dark:text-neutral-400" /> : <ChevronLeft size={20} className="text-neutral-600 dark:text-neutral-400" />}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto">
        {error && (
          <div className="px-4 py-2 mt-2 text-danger-600 bg-danger-100 dark:text-danger-400 dark:bg-danger-900 rounded-lg">
            <AlertCircle className="inline-block mr-2" size={20} />
            {error}
          </div>
        )}
        {menuItems.map((item) => (
          <div key={item.id}>
            <Link
              to={item.url}
              className={`
                flex items-center px-4 py-2 mt-2 text-neutral-600 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-dark-blue-700 rounded-lg
                ${location.pathname === item.url ? 'bg-neutral-200 dark:bg-dark-blue-700' : ''}
              `}
            >
              {React.createElement(getIcon(item.icon), { className: "w-6 h-6" })}
              {!minimized && <span className="mx-4">{item.name}</span>}
            </Link>
          </div>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;