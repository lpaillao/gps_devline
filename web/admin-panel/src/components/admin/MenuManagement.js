import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/solid';

const MenuManagement = () => {
  const [menuItems, /*setMenuItems*/] = useState([
    { id: 1, name: 'Dashboard', path: '/' },
    { id: 2, name: 'Users', path: '/users' },
    { id: 3, name: 'Vehicles', path: '/vehicles' },
  ]);
  const { text, bg } = useTheme();

  const handleAddMenuItem = () => {
    // Implement add functionality
  };

  const handleEditMenuItem = (id) => {
    // Implement edit functionality
  };

  const handleDeleteMenuItem = (id) => {
    // Implement delete functionality
  };

  return (
    <div>
      <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>Menu Management</h2>
      <button
        onClick={handleAddMenuItem}
        className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center mb-4`}
      >
        <PlusIcon className="w-5 h-5 mr-2" />
        Add Menu Item
      </button>
      <ul className="space-y-2">
        {menuItems.map((item) => (
          <li key={item.id} className={`${bg.primary} rounded-lg p-3 flex justify-between items-center`}>
            <span className={text.primary}>{item.name} - {item.path}</span>
            <div className="flex space-x-2">
              <button
                onClick={() => handleEditMenuItem(item.id)}
                className="p-1 rounded-full bg-blue-500 text-white hover:bg-blue-600"
              >
                <PencilIcon className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDeleteMenuItem(item.id)}
                className="p-1 rounded-full bg-red-500 text-white hover:bg-red-600"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MenuManagement;