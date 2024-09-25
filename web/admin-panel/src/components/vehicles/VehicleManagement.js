import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import DeviceList from './DeviceList';
import DeviceDetails from './DeviceDetails';
import MapComponent from './MapComponent';
import { API_BASE_URL, GPS_SERVER_URL } from '../../config';

const VehicleManagement = () => {
  const [devices, setDevices] = useState([]);
  const [connectedDevices, setConnectedDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [routePoints, setRoutePoints] = useState([]);
  const [pointLimit, setPointLimit] = useState(100);
  const [error, setError] = useState(null);
  const [liveTracking, setLiveTracking] = useState(false);
  const [socketConnected, setSocketConnected] = useState(false);  // Estado para el socket
  const socketRef = useRef(null);
  const { user } = useAuth();
  const { text, bg } = useTheme();

  // Maneja las actualizaciones del GPS cuando se recibe un evento 'gps_update'
  const handleGPSUpdate = useCallback((data) => {
    console.log('Received GPS update:', data);
    if (data.imei === selectedDevice?.imei) {
      const { Latitude, Longitude } = data.data.Location;
      setRoutePoints(prevPoints => [...prevPoints, [Latitude, Longitude]]);
    }
  }, [selectedDevice]);

  // Conectar al servidor de GPS usando Socket.IO
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

    // Maneja la respuesta de suscripción y las actualizaciones de GPS
    socketRef.current.on('subscribed', (data) => {
      console.log(`Successfully subscribed to IMEI: ${data.imei}`);
    });

    socketRef.current.on('gps_update', handleGPSUpdate);
  }, [handleGPSUpdate]);

  // Desconectar el socket
  const disconnectSocket = useCallback(() => {
    if (socketRef.current) {
      console.log('Disconnecting socket...');
      socketRef.current.disconnect();
      socketRef.current = null;
      setSocketConnected(false);
    }
  }, []);

  // Suscribirse al IMEI seleccionado
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

  // Obtener el historial de rutas de un dispositivo
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

  // Manejar la selección de un dispositivo
  const handleDeviceSelect = useCallback((device) => {
    setSelectedDevice(device);
    setLiveTracking(false);
    fetchDeviceRoute(device.imei);
  }, [fetchDeviceRoute]);

  // Cambiar el límite de puntos mostrados en el mapa
  const handlePointLimitChange = useCallback((newLimit) => {
    setPointLimit(newLimit);
    if (selectedDevice && !liveTracking) {
      fetchDeviceRoute(selectedDevice.imei);
    }
  }, [selectedDevice, liveTracking, fetchDeviceRoute]);

  // Habilitar o deshabilitar el seguimiento en vivo
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

  // Obtener la lista de dispositivos disponibles
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

  // Obtener los dispositivos conectados al servidor
  const fetchConnectedDevices = useCallback(async () => {
    try {
      const response = await axios.get(`${GPS_SERVER_URL}/connected_devices`);
      setConnectedDevices(response.data);
    } catch (error) {
      console.error('Error fetching connected devices:', error);
    }
  }, []);

  // Efecto para conectar el socket y obtener dispositivos al cargar el componente
  useEffect(() => {
    connectSocket();
    fetchDevices();
    fetchConnectedDevices();

    return () => {
      disconnectSocket();
    };
  }, [connectSocket, disconnectSocket, fetchDevices, fetchConnectedDevices]);

  return (
    <div className="flex flex-col lg:flex-row h-full gap-6">
      <DeviceList 
        devices={devices} 
        connectedDevices={connectedDevices}
        onSelectDevice={handleDeviceSelect} 
        selectedDevice={selectedDevice}
      />
      <div className="w-full lg:w-3/4 space-y-6">
        {error && <div className={`${text.error} mb-4`}>{error}</div>}
        <MapComponent routePoints={routePoints} liveTracking={liveTracking} />
        {selectedDevice && (
          <>
            <DeviceDetails 
              device={selectedDevice} 
              pointLimit={pointLimit} 
              onPointLimitChange={handlePointLimitChange}
              liveTracking={liveTracking}
            />
            {connectedDevices.includes(selectedDevice.imei) && (
              <button
                onClick={toggleLiveTracking}
                className={`px-4 py-2 rounded-md ${liveTracking ? bg.secondary : bg.primary} ${text.primary}`}
              >
                {liveTracking ? 'Stop Live Tracking' : 'Start Live Tracking'}
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default VehicleManagement;
