import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/solid';

const UserList = ({ users, onSelectUser, onDeleteUser }) => {
  const { text, bg } = useTheme();

  return (
    <div className={`${bg.secondary} rounded-xl shadow-lg p-6 w-full lg:w-2/3`}>
      <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>User List</h2>
      <ul className="space-y-4">
        {users.map((user) => (
          <li key={user.id} className={`${bg.primary} rounded-lg p-4 flex justify-between items-center`}>
            <div>
              <h3 className={`font-semibold ${text.primary}`}>{user.name}</h3>
              <p className={`text-sm ${text.secondary}`}>{user.email}</p>
              <p className={`text-sm ${text.secondary}`}>Role: {user.role}</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => onSelectUser(user)}
                className="p-2 rounded-full bg-blue-500 text-white hover:bg-blue-600"
              >
                <PencilIcon className="w-5 h-5" />
              </button>
              <button
                onClick={() => onDeleteUser(user.id)}
                className="p-2 rounded-full bg-red-500 text-white hover:bg-red-600"
              >
                <TrashIcon className="w-5 h-5" />
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserList;