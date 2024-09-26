import React from 'react';
import { TrashIcon, PencilIcon } from '@heroicons/react/24/solid';
import { useTheme } from '../../contexts/ThemeContext';

const ZoneList = ({ zones, onSelectZone, onDeleteZone }) => {
  const { text, bg } = useTheme();

  return (
    <div className="w-full lg:w-1/2">
      <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>Control Zones</h2>
      <ul className="space-y-2">
        {zones.map((zone) => (
          <li key={zone.id} className={`${bg.secondary} p-4 rounded-lg flex justify-between items-center`}>
            <span className={`${text.primary} font-medium`}>{zone.name}</span>
            <div className="flex space-x-2">
              <button
                onClick={() => onSelectZone(zone)}
                className={`${bg.primary} text-white p-2 rounded-md`}
              >
                <PencilIcon className="w-5 h-5" />
              </button>
              <button
                onClick={() => onDeleteZone(zone.id)}
                className="bg-red-500 text-white p-2 rounded-md"
              >
                <TrashIcon className="w-5 h-5" />
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ZoneList;