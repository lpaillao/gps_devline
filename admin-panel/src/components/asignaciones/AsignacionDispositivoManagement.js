import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import AsignacionDispositivoList from './AsignacionDispositivoList';
import AsignacionDispositivoForm from './AsignacionDispositivoForm';
import { LinkIcon, PlusIcon } from '@heroicons/react/24/solid';
import config from '../../config/config';
const AsignacionDispositivoManagement = () => {
  const [asignaciones, setAsignaciones] = useState([]);
  const [selectedAsignacion, setSelectedAsignacion] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchAsignaciones();
  }, []);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const fetchAsignaciones = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${config.api.baseURL}/api/asignaciones`);
      if (response.data.success) {
        setAsignaciones(response.data.asignaciones);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'fetching asignaciones');
    } finally {
      setLoading(false);
    }
  };

  const handleAddAsignacion = async (newAsignacion) => {
    setLoading(true);
    try {
      const response = await axios.post(`${config.api.baseURL}/api/asignaciones`, newAsignacion);
      if (response.data.success) {
        await fetchAsignaciones();
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'adding asignacion');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateAsignacion = async (updatedAsignacion) => {
    setLoading(true);
    try {
      const response = await axios.put(
        `${config.api.baseURL}/api/asignaciones/${updatedAsignacion.id}`, 
        updatedAsignacion
      );
      if (response.data.success) {
        await fetchAsignaciones();
        setSelectedAsignacion(null);
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'updating asignacion');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAsignacion = async (asignacionId) => {
    if (!window.confirm('¿Está seguro de que desea eliminar esta asignación?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.delete(`${config.api.baseURL}/api/asignaciones/${asignacionId}`);
      if (response.data.success) {
        await fetchAsignaciones();
        if (selectedAsignacion?.id === asignacionId) {
          setSelectedAsignacion(null);
          setIsFormVisible(false);
        }
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'deleting asignacion');
    } finally {
      setLoading(false);
    }
  };

  const handleAddClick = () => {
    setSelectedAsignacion(null);
    setIsFormVisible(true);
    setError(null);
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <LinkIcon className="w-8 h-8 mr-2 text-primary-500" />
          Asignación de Dispositivos
        </h1>
        <button
          onClick={handleAddClick}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center
            hover:opacity-90 transition-opacity disabled:opacity-50`}
          disabled={loading}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Asignación
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading && !isFormVisible && (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <AsignacionDispositivoList
          asignaciones={asignaciones}
          onSelectAsignacion={(asignacion) => {
            setSelectedAsignacion(asignacion);
            setIsFormVisible(true);
            setError(null);
          }}
          onDeleteAsignacion={handleDeleteAsignacion}
          loading={loading}
        />
        
        {(isFormVisible || selectedAsignacion) && (
          <AsignacionDispositivoForm
            asignacion={selectedAsignacion}
            onSubmit={selectedAsignacion ? handleUpdateAsignacion : handleAddAsignacion}
            onCancel={() => {
              setSelectedAsignacion(null);
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

export default AsignacionDispositivoManagement;