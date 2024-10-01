import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import DeviceList from './DeviceList';
import DeviceDetails from './DeviceDetails';
import MapComponent from './MapComponent';
import { API_BASE_URL, GPS_SERVER_URL } from '../../config';
import { TruckIcon, MapIcon, ChartBarIcon } from '@heroicons/react/24/solid';
import { motion, AnimatePresence } from 'framer-motion';

const VehicleManagement = () => {
  const [devices, setDevices] = useState([]);
  const [connectedDevices, setConnectedDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [routePoints, setRoutePoints] = useState([]);
  const [error, setError] = useState(null);
  const [liveTracking, setLiveTracking] = useState(false);
  const [socketConnected, setSocketConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('map');
  const [historyPoint, setHistoryPoint] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [pointLimit, setPointLimit] = useState(100);
  const socketRef = useRef(null);
  const { user } = useAuth();
  const { isDarkMode } = useTheme();

  const handleGPSUpdate = useCallback((data) => {
    console.log('Received GPS update:', data);
    if (data.imei === selectedDevice?.imei) {
      const { Latitude, Longitude } = data.data.Location;
      setRoutePoints(prevPoints => [...prevPoints, [Latitude, Longitude]]);
    }
  }, [selectedDevice]);

  const connectSocket = useCallback(() => {
    console.log('Attempting to connect to socket...');
    socketRef.current = io(GPS_SERVER_URL, {
      transports: ['websocket'],
      upgrade: false,
    });

    socketRef.current.on('connect', () => {
      console.log('Successfully connected to GPS server');
      setSocketConnected(true);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from GPS server');
      setSocketConnected(false);
    });

    socketRef.current.on('error', (error) => {
      console.error('Socket connection error:', error);
      setError('Failed to connect to GPS server. Please try again later.');
    });

    socketRef.current.on('subscribed', (data) => {
      console.log(`Successfully subscribed to IMEI: ${data.imei}`);
    });

    socketRef.current.on('gps_update', handleGPSUpdate);
  }, [handleGPSUpdate]);

  const disconnectSocket = useCallback(() => {
    if (socketRef.current) {
      console.log('Disconnecting socket...');
      socketRef.current.disconnect();
      socketRef.current = null;
      setSocketConnected(false);
    }
  }, []);

  const subscribeToIMEI = useCallback((imei) => {
    if (socketRef.current && socketConnected) {
      console.log(`Attempting to subscribe to IMEI: ${imei}`);
      socketRef.current.emit('subscribe', imei, (response) => {
        if (response && response.success) {
          console.log(`Successfully subscribed to IMEI: ${imei}`);
        } else {
          console.error(`Failed to subscribe to IMEI: ${imei}`, response ? response.error : 'Unknown error');
        }
      });
    } else {
      console.error('Socket is not connected. Cannot subscribe.');
    }
  }, [socketConnected]);

  const fetchDeviceRoute = useCallback(async (imei) => {
    try {
      setError(null);
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      const response = await axios.get(`${GPS_SERVER_URL}/gps/${imei}/history?start_date=${startDate}&end_date=${endDate}&limit=${pointLimit}`);
      if (response.data && response.data.length > 0) {
        setRoutePoints(response.data.map(point => [point.latitude, point.longitude]));
      } else {
        setRoutePoints([]);
        setError('No route data available for this device.');
      }
    } catch (error) {
      console.error('Error fetching device route:', error);
      setRoutePoints([]);
      setError('Error fetching device route. The device might be offline or not sending data.');
    }
  }, [pointLimit]);

  const handleDeviceSelect = useCallback((device) => {
    setSelectedDevice(device);
    setLiveTracking(false);
    setHistoryPoint(null);
    fetchDeviceRoute(device.imei);
    setActiveTab('map');
  }, [fetchDeviceRoute]);


  const handleHistoryUpdate = useCallback((newHistoryData) => {
    setHistoryData(newHistoryData);
    if (Array.isArray(newHistoryData) && newHistoryData.length > 0) {
      setRoutePoints(newHistoryData.map(point => [point.latitude, point.longitude]));
      setHistoryPoint(null);
    } else if (newHistoryData) {
      setHistoryPoint(newHistoryData);
    }
  }, []);

  const handlePointLimitChange = useCallback((newLimit) => {
    setPointLimit(newLimit);
  }, []);

  const toggleLiveTracking = useCallback(() => {
    if (liveTracking) {
      setLiveTracking(false);
      if (selectedDevice) {
        fetchDeviceRoute(selectedDevice.imei);
      }
    } else {
      setLiveTracking(true);
      if (selectedDevice) {
        subscribeToIMEI(selectedDevice.imei);
      }
    }
  }, [liveTracking, selectedDevice, fetchDeviceRoute, subscribeToIMEI]);

  const fetchDevices = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}?action=getAllDispositivosGPS`, { withCredentials: true });
      if (response.data.success) {
        setDevices(response.data.dispositivos);
      }
    } catch (error) {
      console.error('Error fetching devices:', error);
      setError('Error fetching devices. Please try again later.');
    }
  }, []);

  const fetchConnectedDevices = useCallback(async () => {
    try {
      const response = await axios.get(`${GPS_SERVER_URL}/connected_devices`);
      setConnectedDevices(response.data);
    } catch (error) {
      console.error('Error fetching connected devices:', error);
    }
  }, []);

  useEffect(() => {
    connectSocket();
    fetchDevices();
    fetchConnectedDevices();

    return () => {
      disconnectSocket();
    };
  }, [connectSocket, disconnectSocket, fetchDevices, fetchConnectedDevices]);

return (
    <div className="min-h-screen p-6 bg-neutral-50 dark:bg-dark-blue-900 text-neutral-900 dark:text-neutral-50">
      <h1 className="text-3xl font-bold mb-6 flex items-center text-primary-600 dark:text-primary-400">
        <TruckIcon className="w-8 h-8 mr-2" />
        Gestión de Vehículos
      </h1>
      <div className="flex flex-col lg:flex-row gap-6">
        <DeviceList 
          devices={devices} 
          connectedDevices={connectedDevices}
          onSelectDevice={handleDeviceSelect} 
          selectedDevice={selectedDevice}
        />
        <div className="w-full lg:w-3/4 space-y-6">
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-100 p-4 rounded-md shadow-md"
            >
              {error}
            </motion.div>
          )}
          {selectedDevice && (
            <>
              <div className="bg-white dark:bg-dark-blue-800 rounded-xl shadow-lg p-4 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-neutral-800 dark:text-neutral-100">
                  {selectedDevice.imei} - {selectedDevice.modelo}
                </h2>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setActiveTab('map')}
                    className={`px-4 py-2 rounded-md transition-colors ${
                      activeTab === 'map' 
                        ? 'bg-primary-500 dark:bg-primary-600 text-white' 
                        : 'bg-neutral-200 dark:bg-dark-blue-700 text-neutral-700 dark:text-neutral-200'
                    }`}
                  >
                    <MapIcon className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setActiveTab('details')}
                    className={`px-4 py-2 rounded-md transition-colors ${
                      activeTab === 'details' 
                        ? 'bg-primary-500 dark:bg-primary-600 text-white' 
                        : 'bg-neutral-200 dark:bg-dark-blue-700 text-neutral-700 dark:text-neutral-200'
                    }`}
                  >
                    <TruckIcon className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setActiveTab('stats')}
                    className={`px-4 py-2 rounded-md transition-colors ${
                      activeTab === 'stats' 
                        ? 'bg-primary-500 dark:bg-primary-600 text-white' 
                        : 'bg-neutral-200 dark:bg-dark-blue-700 text-neutral-700 dark:text-neutral-200'
                    }`}
                  >
                    <ChartBarIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="bg-white dark:bg-dark-blue-800 rounded-xl shadow-lg overflow-hidden"
                >
                  {activeTab === 'map' && (
                    <MapComponent 
                      device={selectedDevice}
                      routePoints={routePoints} 
                      liveTracking={liveTracking} 
                      historyPoint={historyPoint}
                      historyData={historyData}
                      onHistoryUpdate={handleHistoryUpdate}
                      pointLimit={pointLimit}
                      onPointLimitChange={handlePointLimitChange}
                    />
                  )}
                  {activeTab === 'details' && (
                    <DeviceDetails 
                      device={selectedDevice}
                    />
                  )}
                  {activeTab === 'stats' && (
                    <div className="p-6">
                      <h3 className="text-xl font-semibold mb-4 text-neutral-800 dark:text-neutral-100">Estadísticas del Vehículo</h3>
                      <p className="text-neutral-600 dark:text-neutral-300">Próximamente: Gráficos y estadísticas detalladas del vehículo.</p>
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>
              {connectedDevices.includes(selectedDevice.imei) && (
                <motion.button
                  onClick={toggleLiveTracking}
                  className={`px-4 py-2 rounded-md ${
                    liveTracking 
                      ? 'bg-warning-500 dark:bg-warning-600 text-white' 
                      : 'bg-success-500 dark:bg-success-600 text-white'
                  } transition-colors`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {liveTracking ? 'Detener Seguimiento en Vivo' : 'Iniciar Seguimiento en Vivo'}
                </motion.button> 
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default VehicleManagement;