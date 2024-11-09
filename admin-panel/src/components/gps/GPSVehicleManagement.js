import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PlusIcon, LinkIcon, MapPinIcon } from '@heroicons/react/24/solid';

const GPSVehicleManagement = () => {
  const [gpsDevices, setGPSDevices] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [selectedGPS, setSelectedGPS] = useState(null);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const { text, bg } = useTheme();

  const handleAddGPS = (e) => {
    e.preventDefault();
    const newGPS = {
      id: Date.now(),
      imei: e.target.imei.value,
      model: e.target.model.value,
      lastPing: new Date().toISOString(),
      vehicleId: null
    };
    setGPSDevices([...gpsDevices, newGPS]);
    e.target.reset();
  };

  const handleAddVehicle = (e) => {
    e.preventDefault();
    const newVehicle = {
      id: Date.now(),
      name: e.target.name.value,
      type: e.target.type.value,
      licensePlate: e.target.licensePlate.value,
      gpsId: null
    };
    setVehicles([...vehicles, newVehicle]);
    e.target.reset();
  };

  const handleLinkGPSToVehicle = () => {
    if (selectedGPS && selectedVehicle) {
      setGPSDevices(gpsDevices.map(gps => 
        gps.id === selectedGPS.id ? {...gps, vehicleId: selectedVehicle.id} : gps
      ));
      setVehicles(vehicles.map(vehicle => 
        vehicle.id === selectedVehicle.id ? {...vehicle, gpsId: selectedGPS.id} : vehicle
      ));
      setSelectedGPS(null);
      setSelectedVehicle(null);
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      <h1 className={`text-2xl font-bold ${text.primary} flex items-center`}>
        <MapPinIcon className="w-8 h-8 mr-2 text-primary-500" />
        GPS & Vehicle Management
      </h1>
      
      <div className="flex flex-col md:flex-row space-y-6 md:space-y-0 md:space-x-6">
        {/* GPS Management */}
        <div className={`${bg.secondary} rounded-xl shadow-lg p-6 flex-1`}>
          <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>GPS Devices</h2>
          <form onSubmit={handleAddGPS} className="mb-4">
            <input type="text" name="imei" placeholder="IMEI" className={`w-full p-2 mb-2 rounded ${bg.primary} ${text.primary}`} required />
            <input type="text" name="model" placeholder="Model" className={`w-full p-2 mb-2 rounded ${bg.primary} ${text.primary}`} required />
            <button type="submit" className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}>
              <PlusIcon className="w-5 h-5 mr-2" />
              Add GPS
            </button>
          </form>
          <ul className="space-y-2">
            {gpsDevices.map(gps => (
              <li 
                key={gps.id} 
                className={`p-2 rounded ${bg.primary} ${text.primary} cursor-pointer ${selectedGPS?.id === gps.id ? 'ring-2 ring-primary-500' : ''}`}
                onClick={() => setSelectedGPS(gps)}
              >
                IMEI: {gps.imei} | Model: {gps.model}
                {gps.vehicleId && <span className="ml-2 text-green-500">Linked</span>}
              </li>
            ))}
          </ul>
        </div>

        {/* Vehicle Management */}
        <div className={`${bg.secondary} rounded-xl shadow-lg p-6 flex-1`}>
          <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>Vehicles</h2>
          <form onSubmit={handleAddVehicle} className="mb-4">
            <input type="text" name="name" placeholder="Vehicle Name" className={`w-full p-2 mb-2 rounded ${bg.primary} ${text.primary}`} required />
            <input type="text" name="type" placeholder="Vehicle Type" className={`w-full p-2 mb-2 rounded ${bg.primary} ${text.primary}`} required />
            <input type="text" name="licensePlate" placeholder="License Plate" className={`w-full p-2 mb-2 rounded ${bg.primary} ${text.primary}`} required />
            <button type="submit" className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center`}>
              <PlusIcon className="w-5 h-5 mr-2" />
              Add Vehicle
            </button>
          </form>
          <ul className="space-y-2">
            {vehicles.map(vehicle => (
              <li 
                key={vehicle.id} 
                className={`p-2 rounded ${bg.primary} ${text.primary} cursor-pointer ${selectedVehicle?.id === vehicle.id ? 'ring-2 ring-primary-500' : ''}`}
                onClick={() => setSelectedVehicle(vehicle)}
              >
                {vehicle.name} | {vehicle.type} | {vehicle.licensePlate}
                {vehicle.gpsId && <span className="ml-2 text-green-500">GPS Linked</span>}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Link GPS to Vehicle */}
      <div className={`${bg.secondary} rounded-xl shadow-lg p-6`}>
        <h2 className={`text-xl font-semibold ${text.primary} mb-4`}>Link GPS to Vehicle</h2>
        <div className="flex items-center space-x-4">
          <div className={`${bg.primary} ${text.primary} p-2 rounded flex-1`}>
            Selected GPS: {selectedGPS ? `IMEI: ${selectedGPS.imei}` : 'None'}
          </div>
          <div className={`${bg.primary} ${text.primary} p-2 rounded flex-1`}>
            Selected Vehicle: {selectedVehicle ? selectedVehicle.name : 'None'}
          </div>
          <button 
            onClick={handleLinkGPSToVehicle}
            disabled={!selectedGPS || !selectedVehicle}
            className={`${bg.primary} text-white px-4 py-2 rounded-lg flex items-center ${(!selectedGPS || !selectedVehicle) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <LinkIcon className="w-5 h-5 mr-2" />
            Link
          </button>
        </div>
      </div>
    </div>
  );
};

export default GPSVehicleManagement;