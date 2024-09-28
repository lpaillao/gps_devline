import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import { MapIcon } from '@heroicons/react/24/solid';
import { GPS_SERVER_URL } from '../../config';
import ZoneList from './ZoneList';
import ZoneForm from './ZoneForm';
import ZoneMap from './ZoneMap';
import Modal from './Modal';
import { toast } from 'react-toastify';

const ControlZonesManagement = () => {
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditingMap, setIsEditingMap] = useState(false);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchZones();
  }, []);

  const fetchZones = async () => {
    try {
      const response = await axios.get(`${GPS_SERVER_URL}/zones`);
      setZones(response.data);
    } catch (error) {
      console.error('Error al obtener zonas de control:', error);
      toast.error('Error al obtener zonas de control');
    }
  };

  const handleAddZone = async (newZone) => {
    try {
      const response = await axios.post(`${GPS_SERVER_URL}/zones`, newZone);
      if (response.status === 201) {
        fetchZones();
        setIsModalOpen(false);
        setSelectedZone(null);
        toast.success('Zona añadida correctamente');
      }
    } catch (error) {
      console.error('Error al añadir zona de control:', error);
      toast.error('Error al añadir zona de control');
    }
  };

  const handleUpdateZone = async (updatedZone) => {
    try {
      const response = await axios.put(`${GPS_SERVER_URL}/zones/${updatedZone.id}`, updatedZone);
      if (response.status === 200) {
        fetchZones();
        setSelectedZone(null);
        setIsModalOpen(false);
        setIsEditingMap(false);
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
        const response = await axios.delete(`${GPS_SERVER_URL}/zones/${zoneId}`);
        if (response.status === 200) {
          fetchZones();
          setSelectedZone(null);
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
    setIsEditingMap(false);
  };

  const handleEditMapClick = () => {
    setIsEditingMap(true);
  };

  const handleMapEdit = (editedZone) => {
    setSelectedZone(editedZone);
  };

  const handleSaveMapEdit = async () => {
    if (selectedZone) {
      try {
        await handleUpdateZone(selectedZone);
      } catch (error) {
        console.error('Error al guardar los cambios del mapa:', error);
        toast.error('Error al guardar los cambios del mapa');
      }
    }
    setIsEditingMap(false);
  };

  return (
    <div className={`flex flex-col h-screen ${bg.primary} ${text.primary}`}>
      <h1 className={`text-2xl font-bold flex items-center mb-6`}>
        <MapIcon className="w-8 h-8 mr-2 text-primary-500" />
        Gestión de Zonas de Control
      </h1>
      <div className="flex flex-1 space-x-6">
        <div className="w-1/4">
          <ZoneList
            zones={zones}
            selectedZone={selectedZone}
            onSelectZone={handleZoneSelect}
            onDeleteZone={handleDeleteZone}
            onAddZone={() => {
              setSelectedZone(null);
              setIsModalOpen(true);
            }}
            onEditZone={() => setIsModalOpen(true)}
            onEditMap={handleEditMapClick}
          />
        </div>
        <div className="w-3/4 flex-1 relative">
          <ZoneMap
            zones={zones}
            selectedZone={selectedZone}
            isEditing={isEditingMap}
            onZoneChange={handleMapEdit}
          />
          {isEditingMap && (
            <div className="absolute top-4 left-4 z-[1000]">
              <button
                onClick={handleSaveMapEdit}
                className={`${bg.primary} text-white px-4 py-2 rounded-lg shadow-md hover:bg-opacity-90 transition-all`}
              >
                Guardar Cambios del Mapa
              </button>
            </div>
          )}
        </div>
      </div>
      {isModalOpen && (
        <Modal onClose={() => setIsModalOpen(false)}>
          <ZoneForm
            zone={selectedZone}
            onSubmit={selectedZone ? handleUpdateZone : handleAddZone}
            onCancel={() => setIsModalOpen(false)}
          />
        </Modal>
      )}
    </div>
  );
};

export default ControlZonesManagement;