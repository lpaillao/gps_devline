import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import UserList from './UserList';
import UserForm from './UserForm';
import { UserIcon, PlusIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid';
import config from '../../config/config';
const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${config.api.baseURL}/api/users`);
      // La API ahora devuelve directamente el array de usuarios
      const userData = Array.isArray(response.data) ? response.data : response.data.users;
      setUsers(userData || []);
    } catch (error) {
      handleError(error, 'fetching users');
    } finally {
      setLoading(false);
    }
  };

  const handleAddUser = async (newUser) => {
    setLoading(true);
    try {
      const response = await axios.post(`${config.api.baseURL}/api/users`, newUser);
      if (response.data.success) {
        await fetchUsers();
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message || 'Failed to create user');
      }
    } catch (error) {
      handleError(error, 'adding user');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (updatedUser) => {
    setLoading(true);
    try {
      const response = await axios.put(
        `${config.api.baseURL}/api/users/${updatedUser.id}`, 
        updatedUser
      );
      if (response.data.success) {
        await fetchUsers();
        setSelectedUser(null);
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message || 'Failed to update user');
      }
    } catch (error) {
      handleError(error, 'updating user');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.delete(`${config.api.baseURL}/api/users/${userId}`);
      if (response.data.success) {
        await fetchUsers();
        if (selectedUser?.id === userId) {
          setSelectedUser(null);
          setIsFormVisible(false);
        }
      } else {
        throw new Error(response.data.message || 'Failed to delete user');
      }
    } catch (error) {
      handleError(error, 'deleting user');
    } finally {
      setLoading(false);
    }
  };

  const handleAddClick = () => {
    setSelectedUser(null);
    setIsFormVisible(true);
    setError(null);
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <UserIcon className="w-8 h-8 mr-2 text-primary-500" />
          User Management
        </h1>
        <button
          onClick={handleAddClick}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center
            hover:opacity-90 transition-opacity disabled:opacity-50`}
          disabled={loading}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add User
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative flex items-center">
          <ExclamationCircleIcon className="w-5 h-5 mr-2" />
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading && !isFormVisible && (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <UserList
          users={users}
          onSelectUser={(user) => {
            setSelectedUser(user);
            setIsFormVisible(true);
            setError(null);
          }}
          onDeleteUser={handleDeleteUser}
          loading={loading}
        />
        
        {(isFormVisible || selectedUser) && (
          <UserForm
            user={selectedUser}
            onSubmit={selectedUser ? handleUpdateUser : handleAddUser}
            onCancel={() => {
              setSelectedUser(null);
              setIsFormVisible(false);
              setError(null);
            }}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
};

export default UserManagement;