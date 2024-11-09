import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import UbicacionList from './UbicacionList';
import UbicacionForm from './UbicacionForm';
import { MapPinIcon, PlusIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid';
import config from '../../config/config';
const UbicacionManagement = () => {
  const [ubicaciones, setUbicaciones] = useState([]);
  const [selectedUbicacion, setSelectedUbicacion] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchUbicaciones();
  }, []);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const fetchUbicaciones = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${config.api.baseURL}/api/ubicaciones`);
      if (response.data.success) {
        const sortedUbicaciones = response.data.ubicaciones.sort((a, b) => 
          new Date(b.fecha_hora) - new Date(a.fecha_hora)
        );
        setUbicaciones(sortedUbicaciones);
      } else {
        throw new Error(response.data.message || 'Failed to fetch locations');
      }
    } catch (error) {
      handleError(error, 'fetching locations');
    } finally {
      setLoading(false);
    }
  };

  const handleAddUbicacion = async (newUbicacion) => {
    setLoading(true);
    try {
      // Asegurarse de que los datos están en el formato correcto
      const formattedUbicacion = {
        ...newUbicacion,
        fecha_hora: new Date(newUbicacion.fecha_hora).toISOString(),
        latitud: parseFloat(newUbicacion.latitud),
        longitud: parseFloat(newUbicacion.longitud),
        velocidad: newUbicacion.velocidad ? parseFloat(newUbicacion.velocidad) : null,
        bateria: newUbicacion.bateria ? parseFloat(newUbicacion.bateria) : null
      };

      const response = await axios.post(`${config.api.baseURL}/api/ubicaciones`, formattedUbicacion);
      
      if (response.data.success) {
        await fetchUbicaciones();
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message || 'Failed to create location');
      }
    } catch (error) {
      handleError(error, 'adding location');
    } finally {
      setLoading(false);
    }
  };

  const handleGetUbicacionesByDispositivo = async (dispositivo_id) => {
    setLoading(true);
    try {
      const response = await axios.get(`${config.api.baseURL}/api/ubicaciones/dispositivo/${dispositivo_id}`);
      if (response.data.success) {
        const sortedUbicaciones = response.data.ubicaciones.sort((a, b) => 
          new Date(b.fecha_hora) - new Date(a.fecha_hora)
        );
        setUbicaciones(sortedUbicaciones);
      } else {
        throw new Error(response.data.message || 'Failed to fetch device locations');
      }
    } catch (error) {
      handleError(error, 'fetching device locations');
    } finally {
      setLoading(false);
    }
  };

  const handleAddClick = () => {
    setSelectedUbicacion(null);
    setIsFormVisible(true);
    setError(null);
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <MapPinIcon className="w-8 h-8 mr-2 text-primary-500" />
          Ubicación Management
        </h1>
        <button
          onClick={handleAddClick}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center
            hover:opacity-90 transition-opacity disabled:opacity-50`}
          disabled={loading}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Ubicación
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative flex items-center">
          <ExclamationCircleIcon className="w-5 h-5 mr-2" />
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading && !isFormVisible && (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <UbicacionList
          ubicaciones={ubicaciones}
          onSelectUbicacion={setSelectedUbicacion}
          onFilterByDispositivo={handleGetUbicacionesByDispositivo}
          onResetFilter={fetchUbicaciones}
          loading={loading}
        />
        
        {(isFormVisible || selectedUbicacion) && (
          <UbicacionForm
            ubicacion={selectedUbicacion}
            onSubmit={handleAddUbicacion}
            onCancel={() => {
              setSelectedUbicacion(null);
              setIsFormVisible(false);
              setError(null);
            }}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
};

export default UbicacionManagement;