import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { ArrowDownTrayIcon } from '@heroicons/react/24/solid';


const SystemSettings = () => {
  const [settings, setSettings] = useState({
    siteName: 'My Admin Panel',
    logoUrl: '/logo.png',
    defaultLanguage: 'en',
    enableNotifications: true,
    maxUsersPerPage: 20,
  });
  const { text, bg } = useTheme();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prevSettings => ({
      ...prevSettings,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Implement save functionality
    console.log('Saving settings:', settings);
  };

  return (
    <div>
      <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>System Settings</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="siteName" className={`block ${text.secondary} mb-1`}>Site Name</label>
          <input
            type="text"
            id="siteName"
            name="siteName"
            value={settings.siteName}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
          />
        </div>
        <div>
          <label htmlFor="logoUrl" className={`block ${text.secondary} mb-1`}>Logo URL</label>
          <input
            type="text"
            id="logoUrl"
            name="logoUrl"
            value={settings.logoUrl}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
          />
        </div>
        <div>
          <label htmlFor="defaultLanguage" className={`block ${text.secondary} mb-1`}>Default Language</label>
          <select
            id="defaultLanguage"
            name="defaultLanguage"
            value={settings.defaultLanguage}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
          </select>
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            id="enableNotifications"
            name="enableNotifications"
            checked={settings.enableNotifications}
            onChange={handleChange}
            className="mr-2"
          />
          <label htmlFor="enableNotifications" className={text.secondary}>Enable Notifications</label>
        </div>
        <div>
          <label htmlFor="maxUsersPerPage" className={`block ${text.secondary} mb-1`}>Max Users Per Page</label>
          <input
            type="number"
            id="maxUsersPerPage"
            name="maxUsersPerPage"
            value={settings.maxUsersPerPage}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
          />
        </div>
        <button
          type="submit"
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}
        >
          <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
          Save Settings
        </button>
      </form>
    </div>
  );
};

export default SystemSettings;