import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';
import { API_BASE_URL } from '../../config';

const UbicacionForm = ({ ubicacion, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    dispositivo_gps_id: '',
    latitud: '',
    longitud: '',
    fecha_hora: '',
    velocidad: '',
    bateria: '',
  });
  const [dispositivos, setDispositivos] = useState([]);
  const { text, bg } = useTheme();

  useEffect(() => {
    if (ubicacion) {
      setFormData(ubicacion);
    }
    fetchDispositivos();
  }, [ubicacion]);

  const fetchDispositivos = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllDispositivosGPS`);
      if (response.data.success) {
        setDispositivos(response.data.dispositivos);
      }
    } catch (error) {
      console.error('Error fetching dispositivos:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="w-full lg:w-1/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>
        {ubicacion ? 'Edit Ubicación' : 'Add Ubicación'}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="dispositivo_gps_id" className={`block ${text.secondary} font-medium mb-1`}>
            Dispositivo GPS
          </label>
          <select
            id="dispositivo_gps_id"
            name="dispositivo_gps_id"
            value={formData.dispositivo_gps_id}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          >
            <option value="">Select a device</option>
            {dispositivos.map((dispositivo) => (
              <option key={dispositivo.id} value={dispositivo.id}>
                {dispositivo.imei}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="latitud" className={`block ${text.secondary} font-medium mb-1`}>
            Latitud
          </label>
          <input
            type="number"
            step="any"
            id="latitud"
            name="latitud"
            value={formData.latitud}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="longitud" className={`block ${text.secondary} font-medium mb-1`}>
            Longitud
          </label>
          <input
            type="number"
            step="any"
            id="longitud"
            name="longitud"
            value={formData.longitud}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="fecha_hora" className={`block ${text.secondary} font-medium mb-1`}>
            Fecha/Hora
          </label>
          <input
            type="datetime-local"
            id="fecha_hora"
            name="fecha_hora"
            value={formData.fecha_hora}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="velocidad" className={`block ${text.secondary} font-medium mb-1`}>
            Velocidad
          </label>
          <input
            type="number"
            step="0.01"
            id="velocidad"
            name="velocidad"
            value={formData.velocidad}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div>
          <label htmlFor="bateria" className={`block ${text.secondary} font-medium mb-1`}>
            Batería
          </label>
          <input
            type="number"
            step="0.01"
            id="bateria"
            name="bateria"
            value={formData.bateria}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
          />
        </div>
        <div className="flex justify-end space-x-2">
          <button
            type="button"
            onClick={onCancel}
            className={`px-4 py-2 rounded-md ${bg.secondary} ${text.primary}`}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`px-4 py-2 rounded-md ${bg.primary} text-white`}
          >
            {ubicacion ? 'Update' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default UbicacionForm;