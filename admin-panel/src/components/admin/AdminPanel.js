import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { CogIcon, Squares2X2Icon, ShieldCheckIcon } from '@heroicons/react/24/solid';
import MenuManagement from './MenuManagement';
import ProfileManagement from './ProfileManagement';
import SystemSettings from './SystemSettings';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('menu');
  const { text, bg } = useTheme();

  const tabs = [
    { id: 'menu', name: 'Menu Management', icon: Squares2X2Icon },
    { id: 'profiles', name: 'Profile Management', icon: ShieldCheckIcon },
    { id: 'settings', name: 'System Settings', icon: CogIcon },
  ];

  return (
    <div className="flex flex-col space-y-6">
      <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
        <CogIcon className="w-8 h-8 mr-2 text-primary-500" />
        Admin Panel
      </h1>
      <div className={`${bg.secondary} rounded-xl shadow-lg p-6`}>
        <div className="flex space-x-4 mb-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-4 py-2 rounded-lg ${
                activeTab === tab.id
                  ? 'bg-primary-500 text-white'
                  : `${bg.primary} ${text.primary}`
              }`}
            >
              <tab.icon className="w-5 h-5 mr-2" />
              {tab.name}
            </button>
          ))}
        </div>
        <div>
          {activeTab === 'menu' && <MenuManagement />}
          {activeTab === 'profiles' && <ProfileManagement />}
          {activeTab === 'settings' && <SystemSettings />}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;