import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import { TruckIcon, BoltIcon, MapPinIcon, ArrowTrendingUpIcon, ClockIcon } from '@heroicons/react/24/solid';
import { GPS_SERVER_URL } from '../../config';
import { motion } from 'framer-motion';

const DeviceDetails = ({ device }) => {
  const [latestData, setLatestData] = useState(null);
  const [error, setError] = useState(null);
  const { isDarkMode } = useTheme();

  const fetchLatestData = useCallback(async () => {
    try {
      const response = await axios.get(`${GPS_SERVER_URL}/gps/${device.imei}/latest`);
      if (response.data && response.data.imei) {
        setLatestData(response.data);
        setError(null);
      } else {
        throw new Error('Datos inválidos recibidos del servidor');
      }
    } catch (error) {
      console.error('Error al obtener los últimos datos del dispositivo:', error);
      setError('No se pueden obtener los últimos datos del dispositivo. El dispositivo podría estar desconectado o no estar enviando datos.');
      setLatestData(null);
    }
  }, [device.imei]);

  useEffect(() => {
    fetchLatestData();
  }, [fetchLatestData]);

  const DataWidget = ({ icon: IconComponent, title, value, color }) => (
    <motion.div 
      className="bg-white dark:bg-dark-blue-700 rounded-xl shadow-md p-4 flex items-center space-x-4"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <div className={`${color} rounded-full p-3`}>
        <IconComponent className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-neutral-600 dark:text-neutral-300 text-sm">{title}</p>
        <p className="text-neutral-900 dark:text-neutral-100 font-semibold text-lg">{value}</p>
      </div>
    </motion.div>
  );

  return (
    <div className="bg-white dark:bg-dark-blue-800 rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-neutral-900 dark:text-neutral-100 flex items-center">
        <TruckIcon className="w-8 h-8 mr-2 text-primary-500" />
        Detalles de {device.imei}
      </h2>
      {error && (
        <motion.div 
          className="text-red-600 dark:text-red-400 mb-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {error}
        </motion.div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        <DataWidget icon={BoltIcon} title="Velocidad" value={`${latestData?.speed || 'N/A'} km/h`} color="bg-blue-500" />
        <DataWidget icon={MapPinIcon} title="Ubicación" value={latestData ? `${latestData.latitude.toFixed(4)}, ${latestData.longitude.toFixed(4)}` : 'N/A'} color="bg-green-500" />
        <DataWidget icon={ArrowTrendingUpIcon} title="Dirección" value={`${latestData?.angle || 'N/A'}°`} color="bg-yellow-500" />
        <DataWidget icon={ClockIcon} title="Última Actualización" value={latestData?.timestamp || 'N/A'} color="bg-purple-500" />
      </div>
    </div>
  );
};

export default DeviceDetails;