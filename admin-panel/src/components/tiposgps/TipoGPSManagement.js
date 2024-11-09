import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import TipoGPSList from './TipoGPSList';
import TipoGPSForm from './TipoGPSForm';
import { TagIcon, PlusIcon } from '@heroicons/react/24/solid';
import config from '../../config/config';
const TipoGPSManagement = () => {
  const [tiposGPS, setTiposGPS] = useState([]);
  const [selectedTipoGPS, setSelectedTipoGPS] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchTiposGPS();
  }, []);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    // Clear error after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  const fetchTiposGPS = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${config.api.baseURL}/api/tipos-gps`);
      if (response.data.success) {
        setTiposGPS(response.data.tipos);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'fetching tipos GPS');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTipoGPS = async (newTipoGPS) => {
    setLoading(true);
    try {
      const response = await axios.post(`${config.api.baseURL}/api/tipos-gps`, newTipoGPS);
      if (response.data.success) {
        await fetchTiposGPS();
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'adding tipo GPS');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTipoGPS = async (updatedTipoGPS) => {
    setLoading(true);
    try {
      const response = await axios.put(
        `${config.api.baseURL}/api/tipos-gps/${updatedTipoGPS.id}`, 
        updatedTipoGPS
      );
      if (response.data.success) {
        await fetchTiposGPS();
        setSelectedTipoGPS(null);
        setIsFormVisible(false);
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'updating tipo GPS');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTipoGPS = async (tipoGPSId) => {
    if (!window.confirm('Are you sure you want to delete this tipo GPS?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.delete(`${config.api.baseURL}/api/tipos-gps/${tipoGPSId}`);
      if (response.data.success) {
        await fetchTiposGPS();
        if (selectedTipoGPS?.id === tipoGPSId) {
          setSelectedTipoGPS(null);
          setIsFormVisible(false);
        }
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'deleting tipo GPS');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <TagIcon className="w-8 h-8 mr-2 text-primary-500" />
          Tipo GPS Management
        </h1>
        <button
          onClick={() => {
            setSelectedTipoGPS(null);
            setIsFormVisible(true);
          }}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center hover:opacity-90 transition-opacity disabled:opacity-50`}
          disabled={loading}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Tipo GPS
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <TipoGPSList
          tiposGPS={tiposGPS}
          onSelectTipoGPS={(tipo) => {
            setSelectedTipoGPS(tipo);
            setIsFormVisible(true);
          }}
          onDeleteTipoGPS={handleDeleteTipoGPS}
          loading={loading}
        />
        
        {(isFormVisible || selectedTipoGPS) && (
          <TipoGPSForm
            tipoGPS={selectedTipoGPS}
            onSubmit={selectedTipoGPS ? handleUpdateTipoGPS : handleAddTipoGPS}
            onCancel={() => {
              setSelectedTipoGPS(null);
              setIsFormVisible(false);
            }}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
};

export default TipoGPSManagement;