import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import UbicacionList from './UbicacionList';
import UbicacionForm from './UbicacionForm';
import { MapPinIcon, PlusIcon } from '@heroicons/react/24/solid';
import { API_BASE_URL } from '../../config';

const UbicacionManagement = () => {
  const [ubicaciones, setUbicaciones] = useState([]);
  const [selectedUbicacion, setSelectedUbicacion] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchUbicaciones();
  }, []);

  const fetchUbicaciones = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllUbicaciones`);
      if (response.data.success) {
        setUbicaciones(response.data.ubicaciones);
      }
    } catch (error) {
      console.error('Error fetching ubicaciones:', error);
    }
  };

  const handleAddUbicacion = async (newUbicacion) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createUbicacion`, newUbicacion);
      if (response.data.success) {
        fetchUbicaciones();
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error adding ubicacion:', error);
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <MapPinIcon className="w-8 h-8 mr-2 text-primary-500" />
          Ubicación Management
        </h1>
        <button
          onClick={() => setIsFormVisible(true)}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Ubicación
        </button>
      </div>
      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <UbicacionList
          ubicaciones={ubicaciones}
          onSelectUbicacion={setSelectedUbicacion}
        />
        {(isFormVisible || selectedUbicacion) && (
          <UbicacionForm
            ubicacion={selectedUbicacion}
            onSubmit={handleAddUbicacion}
            onCancel={() => {
              setSelectedUbicacion(null);
              setIsFormVisible(false);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default UbicacionManagement;