import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PlusIcon, TrashIcon, UsersIcon, MapPinIcon, PencilSquareIcon } from '@heroicons/react/24/solid';

const ZoneList = ({ zones, selectedZone, onSelectZone, onDeleteZone, onAddZone, onEditZone }) => {
  const { isDarkMode, text, bg } = useTheme();

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className={`text-xl font-semibold ${text.primary}`}>Zonas</h2>
        <button
          onClick={onAddZone}
          className={`${bg.primary} text-white p-2 rounded-md flex items-center hover:bg-opacity-90 transition-colors duration-200`}
        >
          <PlusIcon className="w-5 h-5 mr-1" />
          Añadir
        </button>
      </div>
      <ul className="space-y-2 overflow-y-auto max-h-[calc(100vh-200px)]">
        {zones.map((zone) => (
          <li 
            key={zone.id} 
            className={`${isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-white hover:bg-gray-100'} p-4 rounded-lg flex flex-col cursor-pointer transition-colors duration-200 ${selectedZone && selectedZone.id === zone.id ? 'border-2 border-primary-500' : ''}`}
            onClick={() => onSelectZone(zone)}
          >
            <div className="flex justify-between items-center">
              <span className={`${text.primary} font-medium`}>{zone.name}</span>
              <div className="flex space-x-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEditZone(zone);
                  }}
                  className={`${bg.primary} text-white p-2 rounded-md hover:bg-opacity-90 transition-colors duration-200`}
                  title="Editar zona"
                >
                  <PencilSquareIcon className="w-5 h-5" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteZone(zone.id);
                  }}
                  className="bg-red-500 text-white p-2 rounded-md hover:bg-opacity-90 transition-colors duration-200"
                  title="Eliminar zona"
                >
                  <TrashIcon className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="flex space-x-4 mt-2">
              <span className="flex items-center text-sm">
                <UsersIcon className="w-4 h-4 mr-1" />
                {zone.imeis ? zone.imeis.length : 0} IMEIs
              </span>
              <span className="flex items-center text-sm">
                <MapPinIcon className="w-4 h-4 mr-1" />
                {zone.coordinates ? zone.coordinates.length : 0} Puntos
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ZoneList;