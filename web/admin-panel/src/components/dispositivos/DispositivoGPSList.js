import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/solid';

const DispositivoGPSList = ({ dispositivos, onSelectDispositivo, onDeleteDispositivo }) => {
  const { text, bg } = useTheme();

  return (
    <div className="w-full lg:w-2/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>Dispositivos GPS List</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className={`${bg.secondary}`}>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IMEI</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Modelo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Marca</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo GPS</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className={`${bg.primary} divide-y divide-gray-200`}>
            {dispositivos.map((dispositivo) => (
              <tr key={dispositivo.id}>
                <td className="px-6 py-4 whitespace-nowrap">{dispositivo.imei}</td>
                <td className="px-6 py-4 whitespace-nowrap">{dispositivo.modelo}</td>
                <td className="px-6 py-4 whitespace-nowrap">{dispositivo.marca}</td>
                <td className="px-6 py-4 whitespace-nowrap">{dispositivo.tipo_gps}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => onSelectDispositivo(dispositivo)}
                    className="text-indigo-600 hover:text-indigo-900 mr-2"
                  >
                    <PencilIcon className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => onDeleteDispositivo(dispositivo.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <TrashIcon className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DispositivoGPSList;