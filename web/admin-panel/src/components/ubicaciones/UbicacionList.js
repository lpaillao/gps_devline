import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

const UbicacionList = ({ ubicaciones, onSelectUbicacion }) => {
  const { text, bg } = useTheme();

  return (
    <div className="w-full lg:w-2/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>Ubicaciones List</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className={`${bg.secondary}`}>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dispositivo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Latitud</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Longitud</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha/Hora</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Velocidad</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Batería</th>
            </tr>
          </thead>
          <tbody className={`${bg.primary} divide-y divide-gray-200`}>
            {ubicaciones.map((ubicacion) => (
              <tr key={ubicacion.id} onClick={() => onSelectUbicacion(ubicacion)} className="cursor-pointer hover:bg-gray-100">
                <td className="px-6 py-4 whitespace-nowrap">{ubicacion.dispositivo_gps_id}</td>
                <td className="px-6 py-4 whitespace-nowrap">{ubicacion.latitud}</td>
                <td className="px-6 py-4 whitespace-nowrap">{ubicacion.longitud}</td>
                <td className="px-6 py-4 whitespace-nowrap">{new Date(ubicacion.fecha_hora).toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap">{ubicacion.velocidad || 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap">{ubicacion.bateria || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UbicacionList;