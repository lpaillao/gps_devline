import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../../config';
import { useTheme } from '../../../contexts/ThemeContext';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/solid';

const MenuManagement = () => {
  const [menus, setMenus] = useState([]);
  const [newMenu, setNewMenu] = useState({ name: '', url: '', icon: '' });
  const { text, bg, colors } = useTheme();

  useEffect(() => {
    fetchMenus();
  }, []);

  const fetchMenus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllMenus`);
      if (response.data.success) {
        setMenus(response.data.menus);
      }
    } catch (error) {
      console.error('Error fetching menus:', error);
    }
  };

  const handleInputChange = (e) => {
    setNewMenu({ ...newMenu, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createMenu`, newMenu);
      if (response.data.success) {
        setMenus([...menus, response.data.menu]);
        setNewMenu({ name: '', url: '', icon: '' });
      }
    } catch (error) {
      console.error('Error creating menu:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}?action=deleteMenu&id=${id}`);
      if (response.data.success) {
        setMenus(menus.filter(menu => menu.id !== id));
      }
    } catch (error) {
      console.error('Error deleting menu:', error);
    }
  };

  return (
    <div className={`${bg.primary} p-6 rounded-lg shadow-lg`}>
      <h2 className={`text-2xl font-bold mb-6 ${text.primary}`}>Gestión de Menús</h2>
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex flex-wrap -mx-2 mb-4">
          <input
            type="text"
            name="name"
            value={newMenu.name}
            onChange={handleInputChange}
            placeholder="Nombre del menú"
            className={`${bg.secondary} ${text.primary} px-3 py-2 rounded-md w-full sm:w-1/3 m-2`}
          />
          <input
            type="text"
            name="url"
            value={newMenu.url}
            onChange={handleInputChange}
            placeholder="URL del menú"
            className={`${bg.secondary} ${text.primary} px-3 py-2 rounded-md w-full sm:w-1/3 m-2`}
          />
          <input
            type="text"
            name="icon"
            value={newMenu.icon}
            onChange={handleInputChange}
            placeholder="Icono del menú"
            className={`${bg.secondary} ${text.primary} px-3 py-2 rounded-md w-full sm:w-1/3 m-2`}
          />
        </div>
        <button type="submit" className={`${colors.primary} px-4 py-2 rounded-md flex items-center`}>
          <PlusIcon className="w-5 h-5 mr-2" />
          Crear Menú
        </button>
      </form>
      <ul className="space-y-2">
        {menus.map(menu => (
          <li key={menu.id} className={`${bg.secondary} rounded-lg p-4 flex justify-between items-center`}>
            <span className={text.primary}>{menu.name} - {menu.url} - {menu.icon}</span>
            <div className="flex space-x-2">
              <button className={`${colors.info} p-2 rounded-full`}>
                <PencilIcon className="w-4 h-4" />
              </button>
              <button onClick={() => handleDelete(menu.id)} className={`${colors.danger} p-2 rounded-full`}>
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