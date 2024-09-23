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
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchDispositivos();
  }, []);

  const fetchDispositivos = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllDispositivosGPS`);
      if (response.data.success) {
        setDispositivos(response.data.dispositivos);
      }
    } catch (error) {
      console.error('Error fetching dispositivos GPS:', error);
    }
  };

  const handleAddDispositivo = async (newDispositivo) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createDispositivoGPS`, newDispositivo);
      if (response.data.success) {
        fetchDispositivos();
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error adding dispositivo GPS:', error);
    }
  };

  const handleUpdateDispositivo = async (updatedDispositivo) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=updateDispositivoGPS`, updatedDispositivo);
      if (response.data.success) {
        fetchDispositivos();
        setSelectedDispositivo(null);
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error updating dispositivo GPS:', error);
    }
  };

  const handleDeleteDispositivo = async (dispositivoId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}?action=deleteDispositivoGPS&id=${dispositivoId}`);
      if (response.data.success) {
        fetchDispositivos();
      }
    } catch (error) {
      console.error('Error deleting dispositivo GPS:', error);
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
          onClick={() => setIsFormVisible(true)}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Dispositivo GPS
        </button>
      </div>
      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <DispositivoGPSList
          dispositivos={dispositivos}
          onSelectDispositivo={setSelectedDispositivo}
          onDeleteDispositivo={handleDeleteDispositivo}
        />
        {(isFormVisible || selectedDispositivo) && (
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