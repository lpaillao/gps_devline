import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Icon } from 'leaflet';
import { useTheme } from '../../contexts/ThemeContext';
import { 
  TruckIcon, 
  BoltIcon, 
  ClockIcon, 
  MapPinIcon,
  ArrowTrendingUpIcon,
  CalendarIcon
} from '@heroicons/react/24/solid';

let DefaultIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

const vehicles = [
  { id: 1, name: 'Truck 1', type: 'Heavy Duty', status: 'Moving' },
  { id: 2, name: 'Van 1', type: 'Delivery', status: 'Idle' },
  { id: 3, name: 'Car 1', type: 'Passenger', status: 'Moving' },
];

const fakeRoute = [
  [51.505, -0.09],
  [51.51, -0.1],
  [51.51, -0.12],
];

const VehicleManagement = () => {
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const { text, bg, colors } = useTheme();

  const fakeGPSData = {
    speed: 65,
    latitude: 51.505,
    longitude: -0.09,
    heading: 180,
    timestamp: new Date().toLocaleString(),
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'moving':
        return 'bg-green-500';
      case 'idle':
        return 'bg-yellow-500';
      default:
        return 'bg-blue-500';
    }
  };

  const StatusIndicator = ({ status }) => (
    <span className={`px-2 py-1 rounded-full text-xs text-white font-medium ${getStatusColor(status)}`}>
      {status}
    </span>
  );

  const DataWidget = ({ icon: IconComponent, title, value, color }) => (
    <div className={`${bg.secondary} rounded-xl shadow-md p-4 flex items-center space-x-4`}>
      <div className={`${color} rounded-full p-3`}>
        <IconComponent className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className={`${text.secondary} text-sm`}>{title}</p>
        <p className={`${text.primary} font-semibold text-lg`}>{value}</p>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col lg:flex-row h-full gap-6">
      <div className={`w-full lg:w-1/4 ${bg.secondary} rounded-xl shadow-lg p-6 overflow-y-auto`}>
        <h2 className={`text-2xl font-bold mb-6 ${text.primary} flex items-center`}>
          <TruckIcon className="w-8 h-8 mr-2 text-primary-500" />
          Vehicles
        </h2>
        <ul className="space-y-4">
          {vehicles.map((vehicle) => (
            <li
              key={vehicle.id}
              className={`p-4 ${bg.primary} rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md ${
                selectedVehicle?.id === vehicle.id ? 'ring-2 ring-primary-500' : ''
              }`}
              onClick={() => setSelectedVehicle(vehicle)}
            >
              <h3 className={`font-semibold ${text.primary} text-lg`}>{vehicle.name}</h3>
              <p className={`text-sm ${text.secondary} mt-1`}>{vehicle.type}</p>
              <div className="mt-2 flex justify-between items-center">
                <StatusIndicator status={vehicle.status} />
                <TruckIcon className="w-6 h-6 text-primary-500" />
              </div>
            </li>
          ))}
        </ul>
      </div>
      <div className="w-full lg:w-3/4 space-y-6">
        <div className={`${bg.secondary} rounded-xl shadow-lg p-4`}>
          <MapContainer center={[51.505, -0.09]} zoom={13} style={{ height: '400px', width: '100%', borderRadius: '0.75rem' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <Marker position={[51.505, -0.09]} icon={DefaultIcon}>
              <Popup>Vehicle Location</Popup>
            </Marker>
            <Polyline positions={fakeRoute} color="blue" />
          </MapContainer>
        </div>
        {selectedVehicle && (
          <div className={`${bg.secondary} rounded-xl shadow-lg p-6`}>
            <h2 className={`text-2xl font-bold mb-6 ${text.primary} flex items-center`}>
              <TruckIcon className="w-8 h-8 mr-2 text-primary-500" />
              {selectedVehicle.name} Details
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <DataWidget icon={BoltIcon} title="Speed" value={`${fakeGPSData.speed} km/h`} color="bg-blue-500" />
              <DataWidget icon={MapPinIcon} title="Location" value={`${fakeGPSData.latitude}, ${fakeGPSData.longitude}`} color="bg-green-500" />
              <DataWidget icon={ArrowTrendingUpIcon} title="Heading" value={`${fakeGPSData.heading}°`} color="bg-yellow-500" />
              <DataWidget icon={ClockIcon} title="Last Updated" value={fakeGPSData.timestamp} color="bg-purple-500" />
              <DataWidget icon={CalendarIcon} title="Status" value={<StatusIndicator status={selectedVehicle.status} />} color="bg-red-500" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VehicleManagement;