import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { TruckIcon, WifiIcon, BoltIcon, XCircleIcon } from '@heroicons/react/24/solid';
import { motion } from 'framer-motion';

const DeviceList = ({ devices, connectedDevices, onSelectDevice, selectedDevice }) => {
  const { text, bg } = useTheme();

  return (
    <div className={`w-full lg:w-1/4 ${bg.secondary} rounded-xl shadow-lg p-6 overflow-y-auto max-h-[calc(100vh-2rem)]`}>
      <h2 className={`text-2xl font-bold mb-6 ${text.primary} flex items-center`}>
        <TruckIcon className="w-8 h-8 mr-2 text-primary-500" />
        Dispositivos
      </h2>
      <ul className="space-y-4">
        {devices.map((device) => (
          <motion.li
            key={device.id}
            className={`p-4 ${bg.primary} rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md ${
              selectedDevice?.id === device.id ? 'ring-2 ring-primary-500' : ''
            }`}
            onClick={() => onSelectDevice(device)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex justify-between items-center mb-2">
              <h3 className={`font-semibold ${text.primary} text-lg`}>{device.imei}</h3>
              {connectedDevices.includes(device.imei) ? (
                <WifiIcon className="w-6 h-6 text-green-500" title="Conectado" />
              ) : (
                <XCircleIcon className="w-6 h-6 text-red-500" title="Desconectado" />
              )}
            </div>
            <p className={`text-sm ${text.secondary}`}>Modelo: {device.modelo}</p>
            <p className={`text-sm ${text.secondary}`}>Marca: {device.marca}</p>
            <p className={`text-sm ${text.secondary}`}>Tipo: {device.tipo_gps}</p>
            <div className="mt-2 flex justify-between items-center">
              <span className={`text-sm ${connectedDevices.includes(device.imei) ? 'text-green-500' : 'text-red-500'}`}>
                {connectedDevices.includes(device.imei) ? 'Conectado' : 'Desconectado'}
              </span>
              <BoltIcon className="w-6 h-6 text-primary-500" />
            </div>
          </motion.li>
        ))}
      </ul>
    </div>
  );
};

export default DeviceList;