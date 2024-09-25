import React, { useEffect, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Icon } from 'leaflet';

const DefaultIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

const MapUpdater = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};

const MapComponent = ({ routePoints, liveTracking }) => {
  const mapRef = useRef(null);
  const lastPoint = useMemo(() => routePoints.length > 0 ? routePoints[routePoints.length - 1] : [0, 0], [routePoints]);
  const zoom = 13;

  useEffect(() => {
    if (mapRef.current && liveTracking) {
      mapRef.current.setView(lastPoint, zoom);
    }
  }, [lastPoint, liveTracking, zoom]);

  return (
    <div className="rounded-xl shadow-lg overflow-hidden">
      <MapContainer 
        center={lastPoint} 
        zoom={zoom} 
        style={{ height: '400px', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <MapUpdater center={lastPoint} zoom={zoom} />
        {routePoints.length > 0 && (
          <>
            <Polyline positions={routePoints} color="blue" />
            <Marker position={routePoints[0]} icon={DefaultIcon}>
            </Marker>
            <Marker position={lastPoint} icon={DefaultIcon}>
            </Marker>
          </>
        )}
      </MapContainer>
    </div>
  );
};

export default MapComponent;