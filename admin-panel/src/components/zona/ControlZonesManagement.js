import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapIcon, XMarkIcon } from '@heroicons/react/24/solid';
import ZoneList from './ZoneList';
import ZoneForm from './ZoneForm';
import ZoneMap from './ZoneMap';
import { toast } from 'react-toastify';
import config from '../../config/config';

const ControlZonesManagement = () => {
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [mapMode, setMapMode] = useState('view'); // 'view', 'edit', 'create'
  const [newZoneData, setNewZoneData] = useState(null);
  const [showSidebar, setShowSidebar] = useState(false);


  useEffect(() => {
    fetchZones();
  }, []);

  const fetchZones = async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/zones`);
      setZones(response.data);
    } catch (error) {
      console.error('Error al obtener zonas de control:', error);
      toast.error('Error al obtener zonas de control');
    }
  };

  const handleAddZone = async (zoneFormData) => {
    if (!newZoneData || !newZoneData.coordinates || newZoneData.coordinates.length === 0) {
      toast.error('Debe dibujar una zona en el mapa antes de guardar');
      return;
    }

    const newZone = {
      ...zoneFormData,
      coordinates: newZoneData.coordinates
    };

    try {
      const response = await axios.post(`${config.api.baseURL}/api/zones`, newZone);
      if (response.status === 201) {
        fetchZones();
        setSelectedZone(null);
        setMapMode('view');
        setNewZoneData(null);
        setShowSidebar(false);
        toast.success('Zona añadida correctamente');
      }
    } catch (error) {
      console.error('Error al añadir zona de control:', error);
      toast.error('Error al añadir zona de control');
    }
  };

  const handleUpdateZone = async (updatedZone) => {
    try {
      const response = await axios.put(`${config.api.baseURL}/api/zones/${updatedZone.id}`, updatedZone);
      if (response.status === 200) {
        fetchZones();
        setSelectedZone(null);
        setMapMode('view');
        setShowSidebar(false);
        toast.success('Zona actualizada correctamente');
      }
    } catch (error) {
      console.error('Error al actualizar zona de control:', error);
      toast.error('Error al actualizar zona de control');
    }
  };

  const handleDeleteZone = async (zoneId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta zona?')) {
      try {
        const response = await axios.delete(`${config.api.baseURL}/api/zones/${zoneId}`);
        if (response.status === 200) {
          fetchZones();
          setSelectedZone(null);
          setMapMode('view');
          setShowSidebar(false);
          toast.success('Zona eliminada correctamente');
        }
      } catch (error) {
        console.error('Error al eliminar zona de control:', error);
        toast.error('Error al eliminar zona de control');
      }
    }
  };

  const handleZoneSelect = (zone) => {
    setSelectedZone(zone);
    setMapMode('view');
    setShowSidebar(true);
  };

  const handleEditMapClick = () => {
    setMapMode('edit');
    setShowSidebar(true);
  };

  const handleCreateZoneClick = () => {
    setSelectedZone(null);
    setNewZoneData(null);
    setMapMode('create');
    setShowSidebar(true);
  };

  const handleMapEdit = (editedZone) => {
    if (mapMode === 'create') {
      setNewZoneData(editedZone);
    } else {
      setSelectedZone(editedZone);
    }
  };

  const handleCancelEdit = () => {
    setMapMode('view');
    setSelectedZone(null);
    setNewZoneData(null);
    setShowSidebar(false);
  };

  const handleEditZone = (zone) => {
    setSelectedZone(zone);
    setMapMode('edit');
    setShowSidebar(true);
  };

  return (
    <div className="flex flex-col h-screen bg-neutral-50 dark:bg-dark-blue-900 text-neutral-900 dark:text-neutral-50">
      <h1 className="text-2xl font-bold flex items-center mb-6 text-primary-600 dark:text-primary-400">
        <MapIcon className="w-8 h-8 mr-2" />
        Gestión de Zonas de Control
      </h1>
      <div className="flex flex-1 space-x-6">
        <div className="w-1/4">
          <ZoneList
            zones={zones}
            selectedZone={selectedZone}
            onSelectZone={handleZoneSelect}
            onDeleteZone={handleDeleteZone}
            onAddZone={handleCreateZoneClick}
            onEditZone={handleEditZone}
          />
        </div>
        <div className="flex-1 flex">
          <div className={`flex-1 relative ${showSidebar ? 'w-2/3' : 'w-full'}`}>
            <ZoneMap
              zones={zones}
              selectedZone={selectedZone}
              isEditing={mapMode !== 'view'}
              onZoneChange={handleMapEdit}
              mapMode={mapMode}
            />
            <div className="absolute top-4 right-12 z-[1000] bg-white dark:bg-dark-blue-800 p-2 rounded-lg shadow-md">
              <span className="font-bold text-neutral-700 dark:text-neutral-200">
                Modo: {mapMode === 'view' ? 'Visualización' : mapMode === 'edit' ? 'Edición' : 'Creación'}
              </span>
            </div>
          </div>
          {showSidebar && (
            <div className="w-1/3 bg-white dark:bg-dark-blue-800 text-neutral-900 dark:text-neutral-100 p-4 shadow-lg overflow-y-auto transition-all duration-300 ease-in-out">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-primary-600 dark:text-primary-400">
                  {mapMode === 'create' ? 'Crear Nueva Zona' : 'Editar Zona'}
                </h2>
                <button 
                  onClick={handleCancelEdit} 
                  className="text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200 transition-colors duration-200"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>
              <ZoneForm
                zone={mapMode === 'create' ? newZoneData : selectedZone}
                onSubmit={mapMode === 'create' ? handleAddZone : handleUpdateZone}
                onCancel={handleCancelEdit}
                isCreating={mapMode === 'create'}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ControlZonesManagement;