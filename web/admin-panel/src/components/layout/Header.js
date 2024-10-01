import React from 'react';
import { Sun, Moon, Menu, User } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';

const Header = ({ toggleSidebar }) => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const { user } = useAuth();

  return (
    <header className="bg-white dark:bg-dark-blue-800 py-4 px-6 border-b dark:border-dark-blue-700">
      <div className="flex items-center justify-between">
        <button onClick={toggleSidebar} className="text-neutral-500 dark:text-neutral-400 focus:outline-none lg:hidden">
          <Menu className="h-6 w-6" />
        </button>
        <div className="flex items-center">
          <button onClick={toggleDarkMode} className="flex items-center mr-4">
            {isDarkMode ? <Sun className="h-6 w-6 text-neutral-300" /> : <Moon className="h-6 w-6 text-neutral-700" />}
          </button>
          <div className="flex items-center">
            <User className="h-6 w-6 text-neutral-500 dark:text-neutral-400 mr-2" />
            <span className="text-neutral-700 dark:text-neutral-300 text-sm font-medium">{user?.username || 'Guest'}</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;