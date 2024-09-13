import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import UserList from './UserList';
import UserForm from './UserForm';
import { UserIcon, PlusIcon } from '@heroicons/react/24/solid';

const UserManagement = () => {
  const [users, setUsers] = useState([
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User' },
  ]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const { text, bg } = useTheme();

  const handleAddUser = (newUser) => {
    setUsers([...users, { ...newUser, id: users.length + 1 }]);
    setIsFormVisible(false);
  };

  const handleUpdateUser = (updatedUser) => {
    setUsers(users.map(user => user.id === updatedUser.id ? updatedUser : user));
    setSelectedUser(null);
    setIsFormVisible(false);
  };

  const handleDeleteUser = (userId) => {
    setUsers(users.filter(user => user.id !== userId));
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