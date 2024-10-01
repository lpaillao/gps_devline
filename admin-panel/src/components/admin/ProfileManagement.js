import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/solid';

const ProfileManagement = () => {
  const [profiles, /*setProfiles*/] = useState([
    { id: 1, name: 'Admin', permissions: ['read', 'write', 'delete'] },
    { id: 2, name: 'User', permissions: ['read'] },
  ]);
  const { text, bg } = useTheme();

  const handleAddProfile = () => {
    // Implement add functionality
  };

  const handleEditProfile = (id) => {
    // Implement edit functionality
  };

  const handleDeleteProfile = (id) => {
    // Implement delete functionality
  };

  return (
    <div>
      <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>Profile Management</h2>
      <button
        onClick={handleAddProfile}
        className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center mb-4`}
      >
        <PlusIcon className="w-5 h-5 mr-2" />
        Add Profile
      </button>
      <ul className="space-y-2">
        {profiles.map((profile) => (
          <li key={profile.id} className={`${bg.primary} rounded-lg p-3 flex justify-between items-center`}>
            <div>
              <span className={`${text.primary} font-semibold`}>{profile.name}</span>
              <p className={`${text.secondary} text-sm`}>
                Permissions: {profile.permissions.join(', ')}
              </p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleEditProfile(profile.id)}
                className="p-1 rounded-full bg-blue-500 text-white hover:bg-blue-600"
              >
                <PencilIcon className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDeleteProfile(profile.id)}
                className="p-1 rounded-full bg-red-500 text-white hover:bg-red-600"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProfileManagement;