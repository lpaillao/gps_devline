import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { motion } from 'framer-motion';
import { useTheme } from '../../contexts/ThemeContext';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import axios from 'axios';
import { GPS_SERVER_URL } from '../../config';
import { MagnifyingGlassIcon } from '@heroicons/react/24/solid';
import HistorySlider from './HistorySlider';

const startIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const endIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const MapUpdater = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};


const MapComponent = ({
  device,
  routePoints,
  liveTracking,
  historyPoint,
  historyData,
  onHistoryUpdate,
  pointLimit,
  onPointLimitChange
}) => {
  const mapRef = useRef(null);
  const [startDate, setStartDate] = useState(new Date(Date.now() - 24 * 60 * 60 * 1000));
  const [endDate, setEndDate] = useState(new Date());
  const [error, setError] = useState(null);
  const [localHistoryData, setLocalHistoryData] = useState([]);
  const { text, bg } = useTheme();

  const lastPoint = useMemo(() =>
    routePoints.length > 0 ? routePoints[routePoints.length - 1] : [0, 0],
    [routePoints]
  );

  const zoom = 13;

  useEffect(() => {
    console.log('historyData changed:', historyData);
    if (Array.isArray(historyData)) {
      setLocalHistoryData(historyData);
    }
  }, [historyData]);

  useEffect(() => {
    if (mapRef.current && liveTracking) {
      console.log('Updating map view for live tracking');
      mapRef.current.setView(lastPoint, zoom);
    }
  }, [lastPoint, liveTracking, zoom]);

  const handleSlideChange = useCallback((point) => {
    console.log('Slider changed to:', point);
    onHistoryUpdate(point);
  }, [onHistoryUpdate]);

  const fetchHistoryData = useCallback(async () => {
    try {
      const formattedStartDate = startDate.toISOString().split('T')[0];
      const formattedEndDate = endDate.toISOString().split('T')[0];
      console.log('Fetching history data:', { formattedStartDate, formattedEndDate, pointLimit });
      const response = await axios.get(`${GPS_SERVER_URL}/gps/${device.imei}/history?start_date=${formattedStartDate}&end_date=${formattedEndDate}&limit=${pointLimit}`);
      if (response.data && Array.isArray(response.data)) {
        console.log('History data received:', response.data);
        setLocalHistoryData(response.data);
        onHistoryUpdate(response.data[0]); // Update with the first point
        setError(null);
      } else {
        throw new Error('Datos de historial inválidos recibidos del servidor');
      }
    } catch (error) {
      console.error('Error fetching history data:', error);
      setError('No se pueden obtener los datos históricos. Por favor, intente de nuevo.');
      setLocalHistoryData([]);
      onHistoryUpdate(null);
    }
  }, [device.imei, startDate, endDate, pointLimit, onHistoryUpdate]);

  const mapVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.5 } }
  };

  const center = historyPoint ? [historyPoint.latitude, historyPoint.longitude] : lastPoint;

  console.log('Rendering MapComponent:', { historyPointExists: !!historyPoint, historyDataLength: localHistoryData.length });

  return (
    <motion.div
      className="rounded-xl shadow-lg overflow-hidden"
      variants={mapVariants}
      initial="hidden"
      animate="visible"
    >
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '500px', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <MapUpdater center={center} zoom={zoom} />
        {routePoints.length > 0 && !historyPoint && (
          <>
            <Polyline
              positions={routePoints}
              color="blue"
              weight={4}
              opacity={0.7}
              smoothFactor={1}
            />
            <Marker position={routePoints[0]} icon={startIcon} />
            <Marker position={lastPoint} icon={endIcon} />
          </>
        )}
        {historyPoint && (
          <Marker position={[historyPoint.latitude, historyPoint.longitude]} icon={endIcon} />
        )}
      </MapContainer>
      <div className={`${bg.secondary} p-4`}>
        {localHistoryData.length > 0 && (
          <HistorySlider
            historyData={localHistoryData}
            onSlideChange={handleSlideChange}
          />
        )}

        <h3 className={`${text.primary} text-xl font-semibold mb-4 mt-6`}>Búsqueda de Historial</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className={`block ${text.secondary} text-sm font-medium mb-1`}>Fecha de inicio</label>
            <DatePicker
              selected={startDate}
              onChange={date => setStartDate(date)}
              maxDate={new Date()}
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
            />
          </div>
          <div>
            <label className={`block ${text.secondary} text-sm font-medium mb-1`}>Fecha de fin</label>
            <DatePicker
              selected={endDate}
              onChange={date => setEndDate(date)}
              minDate={startDate}
              maxDate={new Date()}
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
            />
          </div>
          <div>
            <label className={`block ${text.secondary} text-sm font-medium mb-1`}>Límite de puntos</label>
            <input
              type="number"
              value={pointLimit}
              onChange={(e) => onPointLimitChange(parseInt(e.target.value))}
              className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
              min="1"
              max="1000"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={fetchHistoryData}
              className="w-full px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-md hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors duration-200 ease-in-out flex items-center justify-center shadow-md"
            >
              <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
              <span className="font-medium">Buscar</span>
            </button>
          </div>
        </div>
        {error && (
          <motion.div
            className={`${text.error} mb-4`}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {error}
          </motion.div>
        )}
        {liveTracking && (
          <p className="text-sm text-green-600 dark:text-green-400 mt-2">
            Seguimiento en vivo activo
          </p>
        )}
      </div>
    </motion.div>
  );
};

export default MapComponent;