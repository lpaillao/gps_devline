import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import UserList from './UserList';
import UserForm from './UserForm';
import { UserIcon, PlusIcon } from '@heroicons/react/24/solid';
import { API_BASE_URL } from '../../config';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllUsers`);
      if (response.data.success) {
        setUsers(response.data.users);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleAddUser = async (newUser) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createUser`, newUser);
      if (response.data.success) {
        fetchUsers();
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error adding user:', error);
    }
  };

  const handleUpdateUser = async (updatedUser) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=updateUser`, updatedUser);
      if (response.data.success) {
        fetchUsers();
        setSelectedUser(null);
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const handleDeleteUser = async (userId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}?action=deleteUser&id=${userId}`);
      if (response.data.success) {
        fetchUsers();
      }
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <UserIcon className="w-8 h-8 mr-2 text-primary-500" />
          User Management
        </h1>
        <button
          onClick={() => setIsFormVisible(true)}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add User
        </button>
      </div>
      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <UserList
          users={users}
          onSelectUser={setSelectedUser}
          onDeleteUser={handleDeleteUser}
        />
        {(isFormVisible || selectedUser) && (
          <UserForm
            user={selectedUser}
            onSubmit={selectedUser ? handleUpdateUser : handleAddUser}
            onCancel={() => {
              setSelectedUser(null);
              setIsFormVisible(false);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default UserManagement;