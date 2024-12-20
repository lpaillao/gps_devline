import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import DeviceList from './DeviceList';
import DeviceDetails from './DeviceDetails';
import MapComponent from './MapComponent';
import { TruckIcon, MapIcon, ChartBarIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid';
import { motion, AnimatePresence } from 'framer-motion';
import config from '../../config/config';
const VehicleManagement = () => {
  const [devices, setDevices] = useState([]);
  const [connectedDevices, setConnectedDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [routePoints, setRoutePoints] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [liveTracking, setLiveTracking] = useState(false);
  const [socketConnected, setSocketConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('map');
  const [historyPoint, setHistoryPoint] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [pointLimit, setPointLimit] = useState(100);
  const socketRef = useRef(null);

  const handleError = (error, action) => {
    console.error(`Error ${action}:`, error);
    const errorMessage = error.response?.data?.message || `Error ${action}. Please try again.`;
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const handleGPSUpdate = useCallback((data) => {
    console.log('Received GPS update:', data);
    if (data.imei === selectedDevice?.imei) {
      const { Latitude, Longitude } = data.data.Location;
      setRoutePoints(prevPoints => [...prevPoints, [Latitude, Longitude]]);
    }
  }, [selectedDevice]);


  const connectSocket = useCallback(() => {
    console.log('Attempting to connect to socket...');
    socketRef.current = io(config.api.baseURL, {
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
      setLoading(true);
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      const response = await axios.get(
        `${config.api.baseURL}/ubicaciones/dispositivo/${imei}?start_date=${startDate}&end_date=${endDate}&limit=${pointLimit}`
      );
      if (response.data.success && response.data.ubicaciones.length > 0) {
        setRoutePoints(response.data.ubicaciones.map(point => [point.latitud, point.longitud]));
      } else {
        setRoutePoints([]);
        setError('No route data available for this device.');
      }
    } catch (error) {
      handleError(error, 'fetching device route');
      setRoutePoints([]);
    } finally {
      setLoading(false);
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
      setRoutePoints(newHistoryData.map(point => [point.latitud, point.longitud]));
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
      setLoading(true);
      const response = await axios.get(`${config.api.baseURL}/api/dispositivos`);
      if (response.data.success) {
        setDevices(response.data.dispositivos);
      } else {
        throw new Error(response.data.message || 'Failed to fetch devices');
      }
    } catch (error) {
      handleError(error, 'fetching devices');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchConnectedDevices = useCallback(async () => {
    try {
      const response = await axios.get(`${config.api.baseURL}/api/gps/connected_devices`);
      if (Array.isArray(response.data)) {
        setConnectedDevices(response.data);
      }
    } catch (error) {
      console.error('Error fetching connected devices:', error);
    }
  }, []);

  useEffect(() => {
    connectSocket();
    fetchDevices();
    fetchConnectedDevices();

    const refreshInterval = setInterval(fetchConnectedDevices, 30000); // Refresh every 30 seconds

    return () => {
      disconnectSocket();
      clearInterval(refreshInterval);
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
          className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-100 p-4 rounded-md shadow-md flex items-center"
        >
          <ExclamationCircleIcon className="w-5 h-5 mr-2" />
          {error}
        </motion.div>
      )}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-center py-4"
        >
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
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