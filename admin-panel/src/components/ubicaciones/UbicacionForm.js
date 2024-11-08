import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';
import { API_BASE_URL } from '../../config';

const UbicacionForm = ({ ubicacion, onSubmit, onCancel, loading }) => {
  const [formData, setFormData] = useState({
    dispositivo_gps_id: '',
    latitud: '',
    longitud: '',
    fecha_hora: '',
    velocidad: '',
    bateria: '',
  });
  const [dispositivos, setDispositivos] = useState([]);
  const [loadingDispositivos, setLoadingDispositivos] = useState(true);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const { text, bg } = useTheme();

  useEffect(() => {
    if (ubicacion) {
      // Formatear la fecha para el input datetime-local
      const formattedUbicacion = {
        ...ubicacion,
        fecha_hora: ubicacion.fecha_hora 
          ? new Date(ubicacion.fecha_hora).toISOString().slice(0, 16)
          : ''
      };
      setFormData(formattedUbicacion);
    }
    fetchDispositivos();
  }, [ubicacion]);

  const fetchDispositivos = async () => {
    setLoadingDispositivos(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/dispositivos`);
      if (response.data.success) {
        setDispositivos(response.data.dispositivos);
      } else {
        throw new Error(response.data.message || 'Failed to fetch devices');
      }
    } catch (error) {
      console.error('Error fetching dispositivos:', error);
      setError('Error loading devices. Please try again.');
    } finally {
      setLoadingDispositivos(false);
    }
  };

  const validateField = (name, value) => {
    switch (name) {
      case 'latitud':
        return !value ? 'Latitude is required' :
          isNaN(value) ? 'Must be a number' :
          value < -90 || value > 90 ? 'Must be between -90 and 90' : '';
      case 'longitud':
        return !value ? 'Longitude is required' :
          isNaN(value) ? 'Must be a number' :
          value < -180 || value > 180 ? 'Must be between -180 and 180' : '';
      case 'velocidad':
        return value && (isNaN(value) || value < 0) ? 'Must be a positive number' : '';
      case 'bateria':
        return value && (isNaN(value) || value < 0 || value > 100) ? 'Must be between 0 and 100' : '';
      case 'dispositivo_gps_id':
        return !value ? 'Device is required' : '';
      case 'fecha_hora':
        return !value ? 'Date/Time is required' : '';
      default:
        return '';
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Validar el campo
    const fieldError = validateField(name, value);
    setFieldErrors(prev => ({
      ...prev,
      [name]: fieldError
    }));

    // Limpiar error general
    if (error) setError(null);
  };

  const validateForm = () => {
    const errors = {};
    Object.keys(formData).forEach(key => {
      const error = validateField(key, formData[key]);
      if (error) errors[key] = error;
    });
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) {
      setError('Please correct the errors before submitting.');
      return;
    }

    // Formatear los datos antes de enviar
    const formattedData = {
      ...formData,
      latitud: parseFloat(formData.latitud),
      longitud: parseFloat(formData.longitud),
      velocidad: formData.velocidad ? parseFloat(formData.velocidad) : null,
      bateria: formData.bateria ? parseFloat(formData.bateria) : null,
      fecha_hora: new Date(formData.fecha_hora).toISOString()
    };

    onSubmit(formattedData);
  };

  if (loadingDispositivos) {
    return (
      <div className="w-full lg:w-1/3 flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="w-full lg:w-1/3">
      <h2 className={`text-xl font-semibold ${text.secondary} mb-4`}>
        {ubicacion ? 'Edit Ubicación' : 'Add Ubicación'}
      </h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="dispositivo_gps_id" className={`block ${text.secondary} font-medium mb-1`}>
            Dispositivo GPS {dispositivos.length === 0 && '(No devices available)'}
          </label>
          <select
            id="dispositivo_gps_id"
            name="dispositivo_gps_id"
            value={formData.dispositivo_gps_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}
              ${fieldErrors.dispositivo_gps_id ? 'border-red-500' : ''}
              ${loading ? 'opacity-50' : ''}`}
            disabled={loading || dispositivos.length === 0}
          >
            <option value="">Select a device</option>
            {dispositivos.map((dispositivo) => (
              <option key={dispositivo.id} value={dispositivo.id}>
                {dispositivo.imei} - {dispositivo.modelo}
              </option>
            ))}
          </select>
          {fieldErrors.dispositivo_gps_id && (
            <p className="mt-1 text-sm text-red-500">{fieldErrors.dispositivo_gps_id}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}
                ${fieldErrors.latitud ? 'border-red-500' : ''}
                ${loading ? 'opacity-50' : ''}`}
              disabled={loading}
            />
            {fieldErrors.latitud && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.latitud}</p>
            )}
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
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}
                ${fieldErrors.longitud ? 'border-red-500' : ''}
                ${loading ? 'opacity-50' : ''}`}
              disabled={loading}
            />
            {fieldErrors.longitud && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.longitud}</p>
            )}
          </div>
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
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}
              ${fieldErrors.fecha_hora ? 'border-red-500' : ''}
              ${loading ? 'opacity-50' : ''}`}
            disabled={loading}
          />
          {fieldErrors.fecha_hora && (
            <p className="mt-1 text-sm text-red-500">{fieldErrors.fecha_hora}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="velocidad" className={`block ${text.secondary} font-medium mb-1`}>
              Velocidad (km/h)
            </label>
            <input
              type="number"
              step="0.01"
              id="velocidad"
              name="velocidad"
              value={formData.velocidad}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}
                ${fieldErrors.velocidad ? 'border-red-500' : ''}
                ${loading ? 'opacity-50' : ''}`}
              disabled={loading}
            />
            {fieldErrors.velocidad && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.velocidad}</p>
            )}
          </div>

          <div>
            <label htmlFor="bateria" className={`block ${text.secondary} font-medium mb-1`}>
              Batería (%)
            </label>
            <input
              type="number"
              step="0.01"
              id="bateria"
              name="bateria"
              value={formData.bateria}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}
                ${fieldErrors.bateria ? 'border-red-500' : ''}
                ${loading ? 'opacity-50' : ''}`}
              disabled={loading}
            />
            {fieldErrors.bateria && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.bateria}</p>
            )}
          </div>
        </div>

        <div className="flex justify-end space-x-2 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className={`px-4 py-2 rounded-md ${bg.secondary} ${text.primary} 
              hover:opacity-80 transition-opacity`}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`px-4 py-2 rounded-md ${bg.primary} text-white 
              hover:opacity-90 transition-opacity
              ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={loading}
          >
            {loading ? 'Processing...' : ubicacion ? 'Update' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default UbicacionForm;