import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { TruckIcon, WifiIcon } from '@heroicons/react/24/solid';

const DeviceList = ({ devices, connectedDevices, onSelectDevice, selectedDevice }) => {
  const { text, bg } = useTheme();

  return (
    <div className={`w-full lg:w-1/4 ${bg.secondary} rounded-xl shadow-lg p-6 overflow-y-auto`}>
      <h2 className={`text-2xl font-bold mb-6 ${text.primary} flex items-center`}>
        <TruckIcon className="w-8 h-8 mr-2 text-primary-500" />
        Devices
      </h2>
      <ul className="space-y-4">
        {devices.map((device) => (
          <li
            key={device.id}
            className={`p-4 ${bg.primary} rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md ${
              selectedDevice?.id === device.id ? 'ring-2 ring-primary-500' : ''
            }`}
            onClick={() => onSelectDevice(device)}
          >
            <div className="flex justify-between items-center mb-2">
              <h3 className={`font-semibold ${text.primary} text-lg`}>{device.imei}</h3>
              {connectedDevices.includes(device.imei) && (
                <WifiIcon className="w-6 h-6 text-green-500" title="Connected" />
              )}
            </div>
            <p className={`text-sm ${text.secondary}`}>Model: {device.modelo}</p>
            <p className={`text-sm ${text.secondary}`}>Brand: {device.marca}</p>
            <p className={`text-sm ${text.secondary}`}>Type: {device.tipo_gps}</p>
            <div className="mt-2 flex justify-between items-center">
              <span className={`text-sm ${text.secondary}`}>
                Status: {connectedDevices.includes(device.imei) ? 'Connected' : 'Disconnected'}
              </span>
              <TruckIcon className="w-6 h-6 text-primary-500" />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DeviceList;