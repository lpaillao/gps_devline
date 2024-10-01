import React, { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { useTheme } from '../../contexts/ThemeContext';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarMinimized, setSidebarMinimized] = useState(false);
  const { isDarkMode } = useTheme();

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const toggleMinimize = () => setSidebarMinimized(!sidebarMinimized);

  return (
    <div className={`flex h-screen overflow-hidden bg-neutral-50 dark:bg-dark-blue-900 text-neutral-900 dark:text-neutral-50`}>
      <div className={`
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        ${sidebarMinimized ? 'w-20' : 'w-64'}
        fixed inset-y-0 left-0 z-30 transition-all duration-300 transform bg-white dark:bg-dark-blue-800 shadow-lg lg:translate-x-0 lg:static lg:inset-0
      `}>
        <Sidebar minimized={sidebarMinimized} toggleMinimize={toggleMinimize} />
      </div>
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header toggleSidebar={toggleSidebar} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-neutral-50 dark:bg-dark-blue-900">
          <div className="container mx-auto px-6 py-8">
            {children}
          </div>
        </main>
        <Footer />
      </div>
    </div>
  );
};

export default Layout;