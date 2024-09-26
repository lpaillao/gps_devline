import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';

const ZoneForm = ({ zone, coordinates, onSubmit, onCancel }) => {
  const [name, setName] = useState('');
  const [selectedImeis, setSelectedImeis] = useState([]);
  const [dispositivos, setDispositivos] = useState([]);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchDispositivos();
    if (zone) {
      setName(zone.name);
      setSelectedImeis(zone.imeis || []);
    } else {
      setName('');
      setSelectedImeis([]);
    }
  }, [zone]);

  const fetchDispositivos = async () => {
    try {
      const response = await axios.get('http://localhost/devline_app/gps_devline/backend/index.php?action=getAllDispositivosGPS');
      if (response.data.success) {
        setDispositivos(response.data.dispositivos);
      }
    } catch (error) {
      console.error('Error fetching dispositivos:', error);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      id: zone ? zone.id : null,
      name,
      coordinates: zone && zone.coordinates.length > 0 ? zone.coordinates : coordinates, // Usamos las coordenadas del mapa si no hay en la zona
      imeis: selectedImeis
    });
  };

  const handleImeiChange = (imei) => {
    setSelectedImeis(prev => 
      prev.includes(imei) 
        ? prev.filter(i => i !== imei) 
        : [...prev, imei]
    );
  };

  return (
    <div className="w-full lg:w-1/2">
      <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>
        {zone ? 'Edit Control Zone' : 'Add Control Zone'}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className={`block ${text.primary} font-medium mb-1`}>
            Zone Name
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={`w-full px-3 py-2 ${bg.secondary} ${text.primary} rounded-md`}
            required
          />
        </div>
        <div>
          <label className={`block ${text.primary} font-medium mb-1`}>
            Associated IMEIs
          </label>
          <div className="max-h-40 overflow-y-auto border border-gray-300 rounded-md p-2">
            {dispositivos.map(dispositivo => (
              <div key={dispositivo.id} className="flex items-center mb-2">
                <input
                  type="checkbox"
                  id={`imei-${dispositivo.id}`}
                  checked={selectedImeis.includes(dispositivo.imei)}
                  onChange={() => handleImeiChange(dispositivo.imei)}
                  className="mr-2"
                />
                <label htmlFor={`imei-${dispositivo.id}`} className={`${text.primary}`}>
                  {dispositivo.imei} - {dispositivo.modelo} ({dispositivo.marca})
                </label>
              </div>
            ))}
          </div>
        </div>
        <div className="flex space-x-4">
          <button
            type="submit"
            className={`${bg.primary} text-white px-4 py-2 rounded-lg`}
          >
            {zone ? 'Update' : 'Add'} Zone
          </button>
          <button
            type="button"
            onClick={onCancel}
            className={`${bg.secondary} ${text.primary} px-4 py-2 rounded-lg`}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default ZoneForm;