import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';

const ZoneForm = ({ zone, onSubmit, onCancel, isCreating }) => {
  const [name, setName] = useState('');
  const [selectedImeis, setSelectedImeis] = useState([]);
  const [dispositivos, setDispositivos] = useState([]);
  const { isDarkMode, text, bg } = useTheme();

  useEffect(() => {
    fetchDispositivos();
    if (zone) {
      setName(zone.name || '');
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
      console.error('Error al obtener dispositivos:', error);
    }
  };

  const handleImeiChange = (imei) => {
    setSelectedImeis(prev => 
      prev.includes(imei) 
        ? prev.filter(i => i !== imei) 
        : [...prev, imei]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      id: zone ? zone.id : null,
      name,
      coordinates: zone ? zone.coordinates : [],
      imeis: selectedImeis
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className={`block ${text.secondary} font-medium mb-1`}>
          Nombre de la Zona
        </label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className={`w-full px-3 py-2 ${isDarkMode ? 'bg-gray-700 text-white' : 'bg-white text-gray-900'} rounded-md border ${isDarkMode ? 'border-gray-600' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-primary-500`}
          required
        />
      </div>
      <div>
        <label className={`block ${text.secondary} font-medium mb-1`}>
          IMEIs Asociados
        </label>
        <div className={`max-h-40 overflow-y-auto ${isDarkMode ? 'bg-gray-700' : 'bg-gray-100'} rounded-md p-2`}>
          {dispositivos.map(dispositivo => (
            <div key={dispositivo.id} className="flex items-center mb-2">
              <input
                type="checkbox"
                id={`imei-${dispositivo.id}`}
                checked={selectedImeis.includes(dispositivo.imei)}
                onChange={() => handleImeiChange(dispositivo.imei)}
                className="mr-2 form-checkbox text-primary-500 focus:ring-primary-500"
              />
              <label htmlFor={`imei-${dispositivo.id}`} className={`${text.primary} text-sm`}>
                {dispositivo.imei} - {dispositivo.modelo} ({dispositivo.marca})
              </label>
            </div>
          ))}
        </div>
      </div>
      <div className="flex space-x-4">
        <button
          type="submit"
          className={`${bg.primary} text-white px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200`}
        >
          {isCreating ? 'Crear Zona' : 'Actualizar Zona'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className={`${isDarkMode ? 'bg-gray-600 text-white' : 'bg-gray-200 text-gray-800'} px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all duration-200`}
        >
          Cancelar
        </button>
      </div>
    </form>
  );
};

export default ZoneForm;