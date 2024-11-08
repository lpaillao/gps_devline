import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../../config';
import { useTheme } from '../../../contexts/ThemeContext';
import { 
  PlusIcon, 
  TrashIcon, 
  PencilIcon,
  XMarkIcon,
  ExclamationCircleIcon,
  UserGroupIcon,
  ListBulletIcon
} from '@heroicons/react/24/solid';

const RoleManagement = () => {
  const [roles, setRoles] = useState([]);
  const [editingRole, setEditingRole] = useState(null);
  const [formData, setFormData] = useState({ name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg, colors } = useTheme();

  useEffect(() => {
    fetchRoles();
  }, []);

  useEffect(() => {
    if (editingRole) {
      setFormData({ name: editingRole.name });
    } else {
      setFormData({ name: '' });
    }
  }, [editingRole]);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const fetchRoles = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/roles`);
      if (response.data.success) {
        setRoles(response.data.roles);
      }
    } catch (error) {
      handleError(error, 'fetching roles');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      return "Role name is required";
    }
    if (formData.name.length < 3) {
      return "Role name must be at least 3 characters long";
    }
    return null;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) setError(null);
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
      if (editingRole) {
        const response = await axios.put(
          `${API_BASE_URL}/roles/${editingRole.id}`, 
          formData
        );
        if (response.data.success) {
          setRoles(roles.map(role => 
            role.id === editingRole.id ? { ...role, ...formData } : role
          ));
          setEditingRole(null);
        }
      } else {
        const response = await axios.post(`${API_BASE_URL}/roles`, formData);
        if (response.data.success) {
          setRoles([...roles, response.data.role]);
        }
      }
      setFormData({ name: '' });
    } catch (error) {
      handleError(error, editingRole ? 'updating role' : 'creating role');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    const role = roles.find(r => r.id === id);
    if (!role) return;

    if (!window.confirm(`Are you sure you want to delete the role "${role.name}"?`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.delete(`${API_BASE_URL}/roles/${id}`);
      if (response.data.success) {
        setRoles(roles.filter(role => role.id !== id));
        if (editingRole?.id === id) {
          setEditingRole(null);
        }
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'deleting role');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`${bg.primary} p-6 rounded-lg shadow-lg space-y-6`}>
      <div className="flex justify-between items-center">
        <h2 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <UserGroupIcon className="w-8 h-8 mr-2" />
          Role Management
        </h2>
        {editingRole && (
          <button
            onClick={() => setEditingRole(null)}
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
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            placeholder="Role name"
            className={`${bg.secondary} ${text.primary} px-4 py-2 rounded-md flex-grow
              focus:ring-2 focus:ring-primary-500 focus:border-transparent
              ${error ? 'border-red-500' : ''}
              ${loading ? 'opacity-50' : ''}`}
            disabled={loading}
          />
          <button
            type="submit"
            className={`${colors.primary} px-4 py-2 rounded-md flex items-center justify-center
              hover:opacity-90 transition-opacity disabled:opacity-50 min-w-[120px]`}
            disabled={loading}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
            ) : (
              <>
                {editingRole ? (
                  <PencilIcon className="w-5 h-5 mr-2" />
                ) : (
                  <PlusIcon className="w-5 h-5 mr-2" />
                )}
                {editingRole ? 'Update' : 'Create'}
              </>
            )}
          </button>
        </div>
      </form>

      {loading && !editingRole && (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      <div className="space-y-2">
        {roles.map(role => (
          <div
            key={role.id}
            className={`${bg.secondary} rounded-lg p-4 flex justify-between items-center
              ${editingRole?.id === role.id ? 'ring-2 ring-primary-500' : ''}
              hover:bg-opacity-90 transition-colors`}
          >
            <div className={`${text.primary} space-y-1`}>
              <div className="font-medium">{role.name}</div>
              {(role.user_count > 0 || role.menu_count > 0) && (
                <div className="text-sm opacity-75 flex items-center space-x-4">
                  {role.user_count > 0 && (
                    <span className="flex items-center">
                      <UserGroupIcon className="w-4 h-4 mr-1" />
                      {role.user_count} users
                    </span>
                  )}
                  {role.menu_count > 0 && (
                    <span className="flex items-center">
                      <ListBulletIcon className="w-4 h-4 mr-1" />
                      {role.menu_count} menus
                    </span>
                  )}
                </div>
              )}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setEditingRole(role)}
                className={`${colors.info} p-2 rounded-full hover:opacity-80 transition-opacity`}
                disabled={loading}
              >
                <PencilIcon className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDelete(role.id)}
                className={`${colors.danger} p-2 rounded-full hover:opacity-80 transition-opacity
                  ${(role.user_count > 0 || role.menu_count > 0) ? 'opacity-50 cursor-not-allowed' : ''}`}
                disabled={loading || role.user_count > 0 || role.menu_count > 0}
                title={
                  role.user_count > 0 || role.menu_count > 0 
                    ? "Cannot delete role that is in use" 
                    : "Delete role"
                }
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

export default RoleManagement;