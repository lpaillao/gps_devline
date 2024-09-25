import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useTheme } from '../../contexts/ThemeContext';
import { TruckIcon, BoltIcon, MapPinIcon, ArrowTrendingUpIcon, ClockIcon, WifiIcon } from '@heroicons/react/24/solid';
import { GPS_SERVER_URL } from '../../config';

const DeviceDetails = ({ device, pointLimit, onPointLimitChange, liveTracking }) => {
  const [latestData, setLatestData] = useState(null);
  const [error, setError] = useState(null);
  const { text, bg } = useTheme();

  const fetchLatestData = useCallback(async () => {
    try {
      const response = await axios.get(`${GPS_SERVER_URL}/gps/${device.imei}/latest`);
      if (response.data && response.data.imei) {
        setLatestData(response.data);
        setError(null);
      } else {
        throw new Error('Invalid data received from server');
      }
    } catch (error) {
      console.error('Error fetching latest device data:', error);
      setError('Unable to fetch latest device data. The device might be offline or not sending data.');
      setLatestData(null);
    }
  }, [device.imei]);

  useEffect(() => {
    if (!liveTracking) {
      fetchLatestData();
    }
  }, [device, liveTracking, fetchLatestData]);

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
    <div className={`${bg.secondary} rounded-xl shadow-lg p-6`}>
      <h2 className={`text-2xl font-bold mb-6 ${text.primary} flex items-center`}>
        <TruckIcon className="w-8 h-8 mr-2 text-primary-500" />
        {device.imei} Details
        {liveTracking && (
          <WifiIcon className="w-6 h-6 ml-2 text-green-500" title="Live Tracking" />
        )}
      </h2>
      {error ? (
        <div className={`${text.error} mb-4`}>{error}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <DataWidget icon={BoltIcon} title="Speed" value={`${latestData?.speed || 'N/A'} km/h`} color="bg-blue-500" />
          <DataWidget icon={MapPinIcon} title="Location" value={latestData ? `${latestData.latitude.toFixed(4)}, ${latestData.longitude.toFixed(4)}` : 'N/A'} color="bg-green-500" />
          <DataWidget icon={ArrowTrendingUpIcon} title="Heading" value={`${latestData?.angle || 'N/A'}°`} color="bg-yellow-500" />
          <DataWidget icon={ClockIcon} title="Last Updated" value={latestData?.timestamp || 'N/A'} color="bg-purple-500" />
        </div>
      )}
      {!liveTracking && (
        <div className="mt-4">
          <label htmlFor="pointLimit" className={`block ${text.secondary} font-medium mb-1`}>
            Number of route points to display:
          </label>
          <input
            type="number"
            id="pointLimit"
            value={pointLimit}
            onChange={(e) => onPointLimitChange(parseInt(e.target.value))}
            className={`w-full px-3 py-2 border rounded-md ${bg.input} ${text.primary}`}
            min="1"
            max="1000"
          />
        </div>
      )}
    </div>
  );
};

export default DeviceDetails;