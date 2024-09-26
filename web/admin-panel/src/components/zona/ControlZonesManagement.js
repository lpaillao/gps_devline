import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import ZoneList from './ZoneList';
import ZoneForm from './ZoneForm';
import { MapIcon, PlusIcon } from '@heroicons/react/24/solid';
import { API_BASE_URL } from '../../config';
import { MapContainer, TileLayer, FeatureGroup, Polygon } from 'react-leaflet';
import { EditControl } from "react-leaflet-draw";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";

const ControlZonesManagement = () => {
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const { text, bg } = useTheme();

  useEffect(() => {
    fetchZones();
  }, []);

  const fetchZones = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllControlZones`);
      if (response.data.success) {
        setZones(response.data.zones);
      }
    } catch (error) {
      console.error('Error fetching control zones:', error);
    }
  };

  const handleAddZone = async (newZone) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=createControlZone`, newZone);
      if (response.data.success) {
        fetchZones();
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error adding control zone:', error);
    }
  };

  const handleUpdateZone = async (updatedZone) => {
    try {
      const response = await axios.post(`${API_BASE_URL}?action=updateControlZone`, updatedZone);
      if (response.data.success) {
        fetchZones();
        setSelectedZone(null);
        setIsFormVisible(false);
      }
    } catch (error) {
      console.error('Error updating control zone:', error);
    }
  };

  const handleDeleteZone = async (zoneId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}?action=deleteControlZone&id=${zoneId}`);
      if (response.data.success) {
        fetchZones();
      }
    } catch (error) {
      console.error('Error deleting control zone:', error);
    }
  };

  const handleCreated = (e) => {
    const { layer } = e;
    const newZone = {
      name: 'New Zone',
      coordinates: layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng])
    };
    handleAddZone(newZone);
  };

  const handleEdited = (e) => {
    const { layers } = e;
    layers.eachLayer((layer) => {
      const editedZone = {
        id: layer.options.id,
        name: layer.options.name,
        coordinates: layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng])
      };
      handleUpdateZone(editedZone);
    });
  };

  const handleDeleted = (e) => {
    const { layers } = e;
    layers.eachLayer((layer) => {
      handleDeleteZone(layer.options.id);
    });
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
          <MapIcon className="w-8 h-8 mr-2 text-primary-500" />
          Control Zones Management
        </h1>
        <button
          onClick={() => setIsFormVisible(true)}
          className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Add Control Zone
        </button>
      </div>
      <div className="flex flex-col lg:flex-row space-y-6 lg:space-y-0 lg:space-x-6">
        <ZoneList
          zones={zones}
          onSelectZone={setSelectedZone}
          onDeleteZone={handleDeleteZone}
        />
        {(isFormVisible || selectedZone) && (
          <ZoneForm
            zone={selectedZone}
            onSubmit={selectedZone ? handleUpdateZone : handleAddZone}
            onCancel={() => {
              setSelectedZone(null);
              setIsFormVisible(false);
            }}
          />
        )}
      </div>
      <div className="w-full h-[500px]">
        <MapContainer center={[-33.4569, -70.6483]} zoom={13} style={{ height: '100%', width: '100%' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <FeatureGroup>
            <EditControl
              position="topright"
              onCreated={handleCreated}
              onEdited={handleEdited}
              onDeleted={handleDeleted}
              draw={{
                rectangle: false,
                circle: false,
                circlemarker: false,
                marker: false,
                polyline: false
              }}
            />
            {zones.map((zone) => (
              <Polygon key={zone.id} positions={zone.coordinates} />
            ))}
          </FeatureGroup>
        </MapContainer>
      </div>
    </div>
  );
};

export default ControlZonesManagement;