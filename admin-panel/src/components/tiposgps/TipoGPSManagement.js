import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import TipoGPSList from './TipoGPSList';
import TipoGPSForm from './TipoGPSForm';
import { TagIcon, PlusIcon } from '@heroicons/react/24/solid';
import { API_BASE_URL } from '../../config';

const TipoGPSManagement = () => {
  const [tiposGPS, setTiposGPS] = useState([]);
  const [selectedTipoGPS, setSelectedTipoGPS] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchTiposGPS();
  }, []);

  const fetchTiposGPS = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllTiposGPS`);
      if (response.data.success) {
        setTiposGPS(response.data.tipos);
      }
    } catch (error) {
      console.error('Error fetching tipos GPS:', error);
    }
  };

  const handleAddTipoGPS = async (newTipoGPS) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createTipoGPS`, newTipoGPS);
      if (response.data.success) {
        fetchTiposGPS();
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error adding tipo GPS:', error);
    }
  };

  const handleUpdateTipoGPS = async (updatedTipoGPS) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=updateTipoGPS`, updatedTipoGPS);
      if (response.data.success) {
        fetchTiposGPS();
        setSelectedTipoGPS(null);
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error updating tipo GPS:', error);
    }
  };

  const handleDeleteTipoGPS = async (tipoGPSId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}?action=deleteTipoGPS&id=${tipoGPSId}`);
      if (response.data.success) {
        fetchTiposGPS();
      }
    } catch (error) {
      console.error('Error deleting tipo GPS:', error);
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
          onClick={() => setIsFormVisible(true)}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Tipo GPS
        </button>
      </div>
      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <TipoGPSList
          tiposGPS={tiposGPS}
          onSelectTipoGPS={setSelectedTipoGPS}
          onDeleteTipoGPS={handleDeleteTipoGPS}
        />
        {(isFormVisible || selectedTipoGPS) && (
          <TipoGPSForm
            tipoGPS={selectedTipoGPS}
            onSubmit={selectedTipoGPS ? handleUpdateTipoGPS : handleAddTipoGPS}
            onCancel={() => {
              setSelectedTipoGPS(null);
              setIsFormVisible(false);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default TipoGPSManagement;