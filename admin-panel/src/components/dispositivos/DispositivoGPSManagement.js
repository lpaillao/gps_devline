import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import DispositivoGPSList from './DispositivoGPSList';
import DispositivoGPSForm from './DispositivoGPSForm';
import { DevicePhoneMobileIcon, PlusIcon } from '@heroicons/react/24/solid';
import { API_BASE_URL } from '../../config';

const DispositivoGPSManagement = () => {
  const [dispositivos, setDispositivos] = useState([]);
  const [selectedDispositivo, setSelectedDispositivo] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchDispositivos();
  }, []);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || 'An unexpected error occurred';
    setError(errorMessage);
    // Clear error after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  const fetchDispositivos = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/dispositivos`);
      if (response.data.success) {
        setDispositivos(response.data.dispositivos);
      }
    } catch (error) {
      handleError(error, 'fetching dispositivos GPS');
    }
  };

  const handleAddDispositivo = async (newDispositivo) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/dispositivos`, newDispositivo);
      if (response.data.success) {
        await fetchDispositivos();
        setIsFormVisible(false);
      }
    } catch (error) {
      handleError(error, 'adding dispositivo GPS');
    }
  };

  const handleUpdateDispositivo = async (updatedDispositivo) => {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/dispositivos/${updatedDispositivo.id}`, 
        updatedDispositivo
      );
      if (response.data.success) {
        await fetchDispositivos();
        setSelectedDispositivo(null);
        setIsFormVisible(false);
      }
    } catch (error) {
      handleError(error, 'updating dispositivo GPS');
    }
  };

  const handleDeleteDispositivo = async (dispositivoId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/dispositivos/${dispositivoId}`);
      if (response.data.success) {
        await fetchDispositivos();
      }
    } catch (error) {
      handleError(error, 'deleting dispositivo GPS');
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <DevicePhoneMobileIcon className="w-8 h-8 mr-2 text-primary-500" />
          Dispositivo GPS Management
        </h1>
        <button
          onClick={() => {
            setSelectedDispositivo(null);
            setIsFormVisible(true);
          }}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center hover:opacity-90 transition-opacity`}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Dispositivo GPS
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <DispositivoGPSList
          dispositivos={dispositivos}
          onSelectDispositivo={(dispositivo) => {
            setSelectedDispositivo(dispositivo);
            setIsFormVisible(true);
          }}
          onDeleteDispositivo={handleDeleteDispositivo}
        />
        
        {isFormVisible && (
          <DispositivoGPSForm
            dispositivo={selectedDispositivo}
            onSubmit={selectedDispositivo ? handleUpdateDispositivo : handleAddDispositivo}
            onCancel={() => {
              setSelectedDispositivo(null);
              setIsFormVisible(false);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default DispositivoGPSManagement;