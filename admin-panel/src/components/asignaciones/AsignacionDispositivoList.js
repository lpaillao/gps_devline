import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/solid';

const AsignacionDispositivoList = ({ asignaciones, onSelectAsignacion, onDeleteAsignacion }) => {
  const { text, bg } = useTheme();

  return (
    <div className="w-full lg:w-2/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>Asignaciones de Dispositivos</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className={`${bg.secondary}`}>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dispositivo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Empresa</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha Asignación</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className={`${bg.primary} divide-y divide-gray-200`}>
            {asignaciones.map((asignacion) => (
              <tr key={asignacion.id}>
                <td className="px-6 py-4 whitespace-nowrap">{asignacion.imei}</td>
                <td className="px-6 py-4 whitespace-nowrap">{asignacion.usuario || 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap">{asignacion.empresa || 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap">{new Date(asignacion.fecha_asignacion).toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => onSelectAsignacion(asignacion)}
                    className="text-indigo-600 hover:text-indigo-900 mr-2"
                  >
                    <PencilIcon className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => onDeleteAsignacion(asignacion.id)}
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

export default AsignacionDispositivoList;