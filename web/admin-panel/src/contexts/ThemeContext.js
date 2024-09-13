import React, { createContext, useState, useEffect, useContext } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const isDark = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(isDark);
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    localStorage.setItem('darkMode', !isDarkMode);
  };

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const theme = {
    isDarkMode,
    toggleDarkMode,
    colors: {
      primary: 'bg-blue-600 text-white',
      secondary: 'bg-teal-500 text-white',
      success: 'bg-green-500 text-white',
      danger: 'bg-red-500 text-white',
      warning: 'bg-yellow-500 text-black',
      info: 'bg-sky-500 text-white',
    },
    text: {
      primary: 'text-gray-900 dark:text-gray-100',
      secondary: 'text-gray-600 dark:text-gray-400',
    },
    bg: {
      primary: 'bg-white dark:bg-gray-800',
      secondary: 'bg-gray-100 dark:bg-gray-700',
    }
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};