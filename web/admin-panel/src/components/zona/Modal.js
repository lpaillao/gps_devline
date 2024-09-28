import React from 'react';
import { XMarkIcon } from '@heroicons/react/24/solid';
import { useTheme } from '../../contexts/ThemeContext';

const Modal = ({ children, onClose }) => {
  const { isDarkMode, bg, text } = useTheme();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-[1000]">
      <div className={`${isDarkMode ? bg.secondary : 'bg-white'} ${text.primary} rounded-lg p-6 w-full max-w-lg shadow-xl`}>
        <div className="flex justify-end mb-4">
          <button 
            onClick={onClose} 
            className={`${text.secondary} hover:${text.primary}`}
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

export default Modal;