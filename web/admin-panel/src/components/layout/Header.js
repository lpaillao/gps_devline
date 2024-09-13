import React from 'react';
import { Sun, Moon, Menu } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

const Header = ({ toggleSidebar }) => {
  const { isDarkMode, toggleDarkMode } = useTheme();

  return (
    <header className="bg-white dark:bg-gray-800 py-4 px-6 border-b dark:border-gray-700">
      <div className="flex items-center justify-between">
        <button onClick={toggleSidebar} className="text-gray-500 focus:outline-none lg:hidden">
          <Menu className="h-6 w-6" />
        </button>
        <div className="flex items-center">
          <button onClick={toggleDarkMode} className="flex items-center mr-4">
            {isDarkMode ? <Sun className="h-6 w-6 text-gray-300" /> : <Moon className="h-6 w-6 text-gray-700" />}
          </button>
          <span className="text-gray-700 dark:text-gray-300 text-sm font-medium">John Doe</span>
        </div>
      </div>
    </header>
  );
};

export default Header;