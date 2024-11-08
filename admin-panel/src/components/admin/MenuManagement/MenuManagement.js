import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../../config';
import { useTheme } from '../../../contexts/ThemeContext';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  XMarkIcon,
  ExclamationCircleIcon 
} from '@heroicons/react/24/solid';

const MenuManagement = () => {
  const [menus, setMenus] = useState([]);
  const [editingMenu, setEditingMenu] = useState(null);
  const [formData, setFormData] = useState({ name: '', url: '', icon: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg, colors } = useTheme();

  useEffect(() => {
    fetchMenus();
  }, []);

  useEffect(() => {
    if (editingMenu) {
      setFormData(editingMenu);
    } else {
      setFormData({ name: '', url: '', icon: '' });
    }
  }, [editingMenu]);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const fetchMenus = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/menus`);
      if (Array.isArray(response.data)) {
        setMenus(response.data);
      } else if (response.data.success && response.data.menus) {
        setMenus(response.data.menus);
      }
    } catch (error) {
      handleError(error, 'fetching menus');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    if (!formData.name.trim()) return "Menu name is required";
    if (!formData.url.trim()) return "Menu URL is required";
    return null;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      if (editingMenu) {
        const response = await axios.put(
          `${API_BASE_URL}/menus/${editingMenu.id}`, 
          formData
        );
        if (response.data.success) {
          setMenus(menus.map(menu => 
            menu.id === editingMenu.id ? { ...menu, ...formData } : menu
          ));
          setEditingMenu(null);
        }
      } else {
        const response = await axios.post(`${API_BASE_URL}/menus`, formData);
        if (response.data.success) {
          setMenus([...menus, response.data.menu]);
        }
      }
      setFormData({ name: '', url: '', icon: '' });
    } catch (error) {
      handleError(error, editingMenu ? 'updating menu' : 'creating menu');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this menu?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.delete(`${API_BASE_URL}/menus/${id}`);
      if (response.data.success) {
        setMenus(menus.filter(menu => menu.id !== id));
        if (editingMenu?.id === id) {
          setEditingMenu(null);
        }
      }
    } catch (error) {
      handleError(error, 'deleting menu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`${bg.primary} p-6 rounded-lg shadow-lg space-y-6`}>
      <div className="flex justify-between items-center">
        <h2 className={`text-2xl font-bold ${text.primary}`}>Menu Management</h2>
        {editingMenu && (
          <button
            onClick={() => setEditingMenu(null)}
            className={`${colors.warning} px-3 py-1 rounded-md flex items-center hover:opacity-80`}
          >
            <XMarkIcon className="w-4 h-4 mr-1" />
            Cancel Edit
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative flex items-center">
          <ExclamationCircleIcon className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            placeholder="Menu name"
            className={`${bg.secondary} ${text.primary} px-4 py-2 rounded-md w-full
              focus:ring-2 focus:ring-primary-500 focus:border-transparent
              ${error && !formData.name ? 'border-red-500' : ''}`}
            disabled={loading}
          />
          <input
            type="text"
            name="url"
            value={formData.url}
            onChange={handleInputChange}
            placeholder="Menu URL"
            className={`${bg.secondary} ${text.primary} px-4 py-2 rounded-md w-full
              focus:ring-2 focus:ring-primary-500 focus:border-transparent
              ${error && !formData.url ? 'border-red-500' : ''}`}
            disabled={loading}
          />
          <input
            type="text"
            name="icon"
            value={formData.icon}
            onChange={handleInputChange}
            placeholder="Menu icon (optional)"
            className={`${bg.secondary} ${text.primary} px-4 py-2 rounded-md w-full
              focus:ring-2 focus:ring-primary-500 focus:border-transparent`}
            disabled={loading}
          />
        </div>
        <button 
          type="submit" 
          className={`${colors.primary} px-4 py-2 rounded-md flex items-center
            hover:opacity-90 transition-opacity disabled:opacity-50`}
          disabled={loading}
        >
          {loading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
          ) : (
            <PlusIcon className="w-5 h-5 mr-2" />
          )}
          {editingMenu ? 'Update Menu' : 'Create Menu'}
        </button>
      </form>

      {loading && !formData.id && (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      <div className="space-y-2">
        {menus.map(menu => (
          <div 
            key={menu.id} 
            className={`${bg.secondary} rounded-lg p-4 flex justify-between items-center
              ${editingMenu?.id === menu.id ? 'ring-2 ring-primary-500' : ''}`}
          >
            <div className={`${text.primary} space-y-1`}>
              <div className="font-medium">{menu.name}</div>
              <div className="text-sm opacity-75">
                URL: {menu.url}
                {menu.icon && <span className="ml-2">Icon: {menu.icon}</span>}
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setEditingMenu(menu)}
                className={`${colors.info} p-2 rounded-full hover:opacity-80 transition-opacity`}
                disabled={loading}
              >
                <PencilIcon className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDelete(menu.id)}
                className={`${colors.danger} p-2 rounded-full hover:opacity-80 transition-opacity`}
                disabled={loading}
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MenuManagement;