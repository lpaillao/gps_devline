import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { motion } from 'framer-motion';

const HistorySlider = ({ historyData, onSlideChange }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    onSlideChange(historyData[currentIndex]);
  }, [currentIndex, historyData, onSlideChange]);

  const handleSliderChange = (event) => {
    setCurrentIndex(parseInt(event.target.value));
  };

  return (
    <motion.div
      className="bg-white dark:bg-dark-blue-800 rounded-xl shadow-lg p-6 mt-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h3 className="text-xl font-semibold mb-4 text-neutral-900 dark:text-neutral-100">Historial de Ubicaciones</h3>
      <div className="relative">
        <input
          type="range"
          min="0"
          max={historyData.length - 1}
          value={currentIndex}
          onChange={handleSliderChange}
          className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer dark:bg-dark-blue-600 focus:outline-none focus:ring-2 focus:ring-primary-500"
          style={{
            background: `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${(currentIndex / (historyData.length - 1)) * 100}%, #E5E7EB ${(currentIndex / (historyData.length - 1)) * 100}%, #E5E7EB 100%)`,
          }}
        />
        <div className="absolute -bottom-6 left-0 right-0 flex justify-between text-xs text-neutral-500 dark:text-neutral-400">
          <span>{historyData[0].timestamp}</span>
          <span>{historyData[historyData.length - 1].timestamp}</span>
        </div>
      </div>
      <div className="mt-8 text-neutral-600 dark:text-neutral-300">
        <p>Fecha y hora: {historyData[currentIndex].timestamp}</p>
        <p>Latitud: {historyData[currentIndex].latitude}</p>
        <p>Longitud: {historyData[currentIndex].longitude}</p>
        <p>Velocidad: {historyData[currentIndex].speed} km/h</p>
      </div>
    </motion.div>
  );
};

export default HistorySlider;