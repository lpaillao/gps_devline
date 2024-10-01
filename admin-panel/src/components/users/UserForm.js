import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';

const UserForm = ({ user, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '', role_id: '2' });
  const { text, bg } = useTheme();

  useEffect(() => {
    if (user) {
      setFormData({ ...user, password: '' });
    } else {
      setFormData({ username: '', email: '', password: '', role_id: '2' });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className={`${bg.secondary} rounded-xl shadow-lg p-6 w-full lg:w-1/3`}>
      <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>
        {user ? 'Edit User' : 'Add User'}
      </h2>
      <div className="space-y-4">
        <div>
          <label htmlFor="username" className={`block ${text.secondary} mb-1`}>Username</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
            required
          />
        </div>
        <div>
          <label htmlFor="email" className={`block ${text.secondary} mb-1`}>Email</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
            required
          />
        </div>
        {!user && (
          <div>
            <label htmlFor="password" className={`block ${text.secondary} mb-1`}>Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`w-full px-3 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
              required={!user}
            />
          </div>
        )}
        <div>
          <label htmlFor="role_id" className={`block ${text.secondary} mb-1`}>Role</label>
          <select
            id="role_id"
            name="role_id"
            value={formData.role_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
          >
            <option value="2">User</option>
            <option value="1">Admin</option>
          </select>
        </div>
      </div>
      <div className="mt-6 flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className={`px-4 py-2 rounded-lg ${bg.primary} ${text.primary} border border-gray-300`}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600"
        >
          {user ? 'Update' : 'Add'}
        </button>
      </div>
    </form>
  );
};

export default UserForm;