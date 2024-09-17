import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../../config';
import { useTheme } from '../../../contexts/ThemeContext';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/solid';

const RoleManagement = () => {
  const [roles, setRoles] = useState([]);
  const [newRole, setNewRole] = useState({ name: '' });
  const { text, bg, colors } = useTheme();

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllRoles`);
      if (response.data.success) {
        setRoles(response.data.roles);
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
    }
  };

  const handleInputChange = (e) => {
    setNewRole({ ...newRole, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createRole`, newRole);
      if (response.data.success) {
        setRoles([...roles, response.data.role]);
        setNewRole({ name: '' });
      }
    } catch (error) {
      console.error('Error creating role:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}?action=deleteRole&id=${id}`);
      if (response.data.success) {
        setRoles(roles.filter(role => role.id !== id));
      }
    } catch (error) {
      console.error('Error deleting role:', error);
    }
  };

  return (
    <div className={`${bg.primary} p-6 rounded-lg shadow-lg`}>
      <h2 className={`text-2xl font-bold mb-6 ${text.primary}`}>Gestión de Roles</h2>
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex flex-wrap -mx-2 mb-4">
          <input
            type="text"
            name="name"
            value={newRole.name}
            onChange={handleInputChange}
            placeholder="Nombre del rol"
            className={`${bg.secondary} ${text.primary} px-3 py-2 rounded-md w-full sm:w-2/3 m-2`}
          />
          <button type="submit" className={`${colors.primary} px-4 py-2 rounded-md flex items-center m-2`}>
            <PlusIcon className="w-5 h-5 mr-2" />
            Crear Rol
          </button>
        </div>
      </form>
      <ul className="space-y-2">
        {roles.map(role => (
          <li key={role.id} className={`${bg.secondary} rounded-lg p-4 flex justify-between items-center`}>
            <span className={text.primary}>{role.name}</span>
            <button onClick={() => handleDelete(role.id)} className={`${colors.danger} p-2 rounded-full`}>
              <TrashIcon className="w-4 h-4" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RoleManagement;