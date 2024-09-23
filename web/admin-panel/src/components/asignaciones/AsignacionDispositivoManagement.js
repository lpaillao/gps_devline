import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import AsignacionDispositivoList from './AsignacionDispositivoList';
import AsignacionDispositivoForm from './AsignacionDispositivoForm';
import { LinkIcon, PlusIcon } from '@heroicons/react/24/solid';
import { API_BASE_URL } from '../../config';

const AsignacionDispositivoManagement = () => {
  const [asignaciones, setAsignaciones] = useState([]);
  const [selectedAsignacion, setSelectedAsignacion] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchAsignaciones();
  }, []);

  const fetchAsignaciones = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllAsignaciones`);
      if (response.data.success) {
        setAsignaciones(response.data.asignaciones);
      }
    } catch (error) {
      console.error('Error fetching asignaciones:', error);
    }
  };

  const handleAddAsignacion = async (newAsignacion) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createAsignacion`, newAsignacion);
      if (response.data.success) {
        fetchAsignaciones();
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error adding asignacion:', error);
    }
  };

  const handleUpdateAsignacion = async (updatedAsignacion) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=updateAsignacion`, updatedAsignacion);
      if (response.data.success) {
        fetchAsignaciones();
        setSelectedAsignacion(null);
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error updating asignacion:', error);
    }
  };

  const handleDeleteAsignacion = async (asignacionId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}?action=deleteAsignacion&id=${asignacionId}`);
      if (response.data.success) {
        fetchAsignaciones();
      }
    } catch (error) {
      console.error('Error deleting asignacion:', error);
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <LinkIcon className="w-8 h-8 mr-2 text-primary-500" />
          Asignación de Dispositivos
        </h1>
        <button
          onClick={() => setIsFormVisible(true)}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Asignación
        </button>
      </div>
      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <AsignacionDispositivoList
          asignaciones={asignaciones}
          onSelectAsignacion={setSelectedAsignacion}
          onDeleteAsignacion={handleDeleteAsignacion}
        />
        {(isFormVisible || selectedAsignacion) && (
          <AsignacionDispositivoForm
            asignacion={selectedAsignacion}
            onSubmit={selectedAsignacion ? handleUpdateAsignacion : handleAddAsignacion}
            onCancel={() => {
              setSelectedAsignacion(null);
              setIsFormVisible(false);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default AsignacionDispositivoManagement;