import React, { useEffect, useState } from 'react';
import { TrashIcon, PencilIcon, PlusIcon } from '@heroicons/react/24/solid';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';
import { GPS_SERVER_URL } from '../../config';

const ZoneList = ({ imei, onSelectZone, onDeleteZone, onAddZone }) => {
  const { text, bg } = useTheme();
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchZones = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${GPS_SERVER_URL}/api/zones/imei/${imei}`);
        setZones(response.data);
        setError(null);
      } catch (error) {
        console.error('Error fetching zones:', error);
        setError('Failed to fetch zones. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (imei) {
      fetchZones();
    }
  }, [imei]);

  const handleDeleteZone = async (zoneId) => {
    if (window.confirm('Are you sure you want to delete this zone?')) {
      try {
        await axios.delete(`${GPS_SERVER_URL}/api/zones/${zoneId}`);
        setZones(zones.filter(zone => zone.id !== zoneId));
        onDeleteZone(zoneId);
      } catch (error) {
        console.error('Error deleting zone:', error);
        setError('Failed to delete zone. Please try again.');
      }
    }
  };

  if (loading) {
    return <div className={`${text.primary}`}>Loading zones...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="w-full lg:w-1/2">
      <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>Control Zones</h2>
      <button
        onClick={onAddZone}
        className={`${bg.primary} text-white p-2 rounded-md mb-4 flex items-center`}
      >
        <PlusIcon className="w-5 h-5 mr-1" />
        Add Zone
      </button>
      {zones.length === 0 ? (
        <p className={`${text.primary}`}>No zones found for this IMEI.</p>
      ) : (
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
                  onClick={() => handleDeleteZone(zone.id)}
                  className="bg-red-500 text-white p-2 rounded-md"
                >
                  <TrashIcon className="w-5 h-5" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ZoneList;