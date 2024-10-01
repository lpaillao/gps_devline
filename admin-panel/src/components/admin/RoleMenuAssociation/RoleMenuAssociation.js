import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../../config';
import { useTheme } from '../../../contexts/ThemeContext';
import { SaveIcon } from '@heroicons/react/24/solid';
import { CheckIcon } from '@heroicons/react/24/solid';


const RoleMenuAssociation = () => {
  const [roles, setRoles] = useState([]);
  const [menus, setMenus] = useState([]);
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedMenus, setSelectedMenus] = useState([]);
  const { text, bg, colors } = useTheme();

  useEffect(() => {
    fetchRoles();
    fetchMenus();
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

  const handleRoleChange = async (e) => {
    const roleId = e.target.value;
    setSelectedRole(roleId);
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getMenusByRoleId&roleId=${roleId}`);
      if (response.data.success) {
        setSelectedMenus(response.data.menus.map(menu => menu.id));
      }
    } catch (error) {
      console.error('Error fetching menus for role:', error);
    }
  };

  const handleMenuToggle = (menuId) => {
    setSelectedMenus(prevSelectedMenus =>
      prevSelectedMenus.includes(menuId)
        ? prevSelectedMenus.filter(id => id !== menuId)
        : [...prevSelectedMenus, menuId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}?action=updateRoleMenus`, {
        roleId: selectedRole,
        menuIds: selectedMenus
      });
      if (response.data.success) {
        alert('Menús actualizados para el rol');
      }
    } catch (error) {
      console.error('Error updating role menus:', error);
    }
  };

  return (
    <div className={`${bg.primary} p-6 rounded-lg shadow-lg`}>
      <h2 className={`text-2xl font-bold mb-6 ${text.primary}`}>Asociación de Menús a Roles</h2>
      <form onSubmit={handleSubmit}>
        <select
          value={selectedRole}
          onChange={handleRoleChange}
          className={`${bg.secondary} ${text.primary} px-3 py-2 rounded-md w-full mb-4`}
        >
          <option value="">Seleccionar Rol</option>
          {roles.map(role => (
            <option key={role.id} value={role.id}>{role.name}</option>
          ))}
        </select>
        <div className={`${bg.secondary} p-4 rounded-lg mb-4`}>
          {menus.map(menu => (
            <label key={menu.id} className={`flex items-center mb-2 ${text.primary}`}>
              <input
                type="checkbox"
                checked={selectedMenus.includes(menu.id)}
                onChange={() => handleMenuToggle(menu.id)}
                className="mr-2"
              />
              {menu.name}
            </label>
          ))}
        </div>
        <button type="submit" className={`${colors.primary} px-4 py-2 rounded-md flex items-center`}>
  <CheckIcon className="w-5 h-5 mr-2" />
  Guardar Cambios
</button>

      </form>
    </div>
  );
};

export default RoleMenuAssociation;