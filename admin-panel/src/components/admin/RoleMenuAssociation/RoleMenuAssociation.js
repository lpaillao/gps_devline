import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../../config/config';
import { useTheme } from '../../../contexts/ThemeContext';
import { 
  CheckIcon,
  ExclamationCircleIcon,
  ListBulletIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/solid';

const RoleMenuAssociation = () => {
  const [roles, setRoles] = useState([]);
  const [menus, setMenus] = useState([]);
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedMenus, setSelectedMenus] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { text, bg, colors } = useTheme();

  useEffect(() => {
    fetchInitialData();
  }, []);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([fetchRoles(), fetchMenus()]);
    } catch (error) {
      handleError(error, 'loading initial data');
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/roles`);
      if (response.data.success) {
        setRoles(response.data.roles);
      }
    } catch (error) {
      throw error;
    }
  };

  const fetchMenus = async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/menus`);
      if (response.data.success) {
        setMenus(response.data.menus);
      }
    } catch (error) {
      throw error;
    }
  };

  const handleRoleChange = async (e) => {
    const roleId = e.target.value;
    setSelectedRole(roleId);
    setLoading(true);
    
    try {
      if (roleId) {
        const response = await axios.get(`${config.api.baseURL}/api/roles/${roleId}/menus`);
        if (response.data.success) {
          // Actualizado para usar menu_ids en lugar de menus
          setSelectedMenus(response.data.menu_ids || []);
        } else {
          throw new Error(response.data.message || 'Failed to fetch menus for role');
        }
      } else {
        setSelectedMenus([]);
      }
    } catch (error) {
      handleError(error, 'fetching menus for role');
      setSelectedMenus([]);
    } finally {
      setLoading(false);
    }
  };

  const handleMenuToggle = (menuId) => {
    setSelectedMenus(prevSelectedMenus =>
      prevSelectedMenus.includes(menuId)
        ? prevSelectedMenus.filter(id => id !== menuId)
        : [...prevSelectedMenus, menuId]
    );
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedRole) {
      setError('Please select a role first');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${config.api.baseURL}/api/roles/${selectedRole}/menus`, {
        menu_ids: selectedMenus  // Ya está en el formato correcto
      });
      
      if (response.data.success) {
        setSuccess('Menus updated successfully');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        throw new Error(response.data.message || 'Failed to update role menus');
      }
    } catch (error) {
      handleError(error, 'updating role menus');
    } finally {
      setLoading(false);
    }
  };

  const filteredMenus = menus.filter(menu => {
    if (!menu?.name || !menu?.url) return false;
    return (
      menu.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      menu.url.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  return (
    <div className={`${bg.primary} p-6 rounded-lg shadow-lg space-y-6`}>
      <div className="flex items-center justify-between">
        <h2 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <ListBulletIcon className="w-8 h-8 mr-2" />
          Menu Role Association
        </h2>
        {selectedRole && (
          <div className={`${text.secondary} text-sm`}>
            Selected Role: <span className="font-semibold">
              {roles.find(r => r.id === parseInt(selectedRole))?.name}
            </span>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative flex items-center">
          <ExclamationCircleIcon className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative flex items-center">
          <CheckIcon className="w-5 h-5 mr-2" />
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <select
          value={selectedRole}
          onChange={handleRoleChange}
          className={`${bg.secondary} ${text.primary} px-4 py-2 rounded-md w-full
            focus:ring-2 focus:ring-primary-500 focus:border-transparent
            ${loading ? 'opacity-50' : ''}`}
          disabled={loading}
        >
          <option value="">Select a Role</option>
          {roles.map(role => (
            <option key={role.id} value={role.id}>
              {role.name} {role.user_count > 0 && `(${role.user_count} users)`}
            </option>
          ))}
        </select>

        <div className="relative">
          <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search menus..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`${bg.secondary} ${text.primary} pl-10 pr-4 py-2 rounded-md w-full
              focus:ring-2 focus:ring-primary-500 focus:border-transparent`}
          />
        </div>

        <div className={`${bg.secondary} p-4 rounded-lg max-h-96 overflow-y-auto space-y-2`}>
          {loading ? (
            <div className="flex justify-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
          ) : filteredMenus.length === 0 ? (
            <div className={`${text.secondary} text-center py-4`}>
              No menus found
            </div>
          ) : (
            filteredMenus.map(menu => (
              <label 
                key={menu.id} 
                className={`flex items-center p-2 rounded-md hover:bg-opacity-50 cursor-pointer
                  ${selectedMenus.includes(menu.id) ? bg.primary : ''}`}
              >
                <input
                  type="checkbox"
                  checked={selectedMenus.includes(menu.id)}
                  onChange={() => handleMenuToggle(menu.id)}
                  className="mr-3 h-4 w-4"
                  disabled={loading}
                />
                <div className={`${text.primary} flex-grow`}>
                  <div className="font-medium">{menu.name}</div>
                  <div className="text-sm opacity-75">{menu.url}</div>
                </div>
                {menu.icon && (
                  <div className={`${text.secondary} text-sm ml-2`}>
                    {menu.icon}
                  </div>
                )}
              </label>
            ))
          )}
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className={`${colors.primary} px-6 py-2 rounded-md flex items-center
              hover:opacity-90 transition-opacity disabled:opacity-50`}
            disabled={loading || !selectedRole}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
            ) : (
              <CheckIcon className="w-5 h-5 mr-2" />
            )}
            Save Changes
          </button>
        </div>
      </form>
    </div>
  );
};

export default RoleMenuAssociation;