import React, { useEffect } from 'react';
import { MapContainer, TileLayer, FeatureGroup, Polygon, ZoomControl, ScaleControl, Tooltip } from 'react-leaflet';
import { EditControl } from "react-leaflet-draw";
import L from 'leaflet';
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";

const ZoneMap = ({ zones, selectedZone, isEditing, onZoneChange }) => {
  useEffect(() => {
    if (selectedZone && window.map) {
      const bounds = selectedZone.coordinates.map(coord => [coord[0], coord[1]]);
      window.map.fitBounds(bounds);
    }
  }, [selectedZone]);

  const handleCreated = (e) => {
    const { layer } = e;
    const newCoordinates = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);
    onZoneChange({ ...selectedZone, coordinates: newCoordinates });
  };

  const handleEdited = (e) => {
    const { layers } = e;
    layers.eachLayer((layer) => {
      const editedZone = {
        ...selectedZone,
        coordinates: layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng])
      };
      onZoneChange(editedZone);
    });
  };

  const getZoneCenter = (coordinates) => {
    const bounds = L.latLngBounds(coordinates);
    return bounds.getCenter();
  };

  return (
    <div className="h-full">
      <MapContainer 
        center={[-33.4569, -70.6483]} 
        zoom={13} 
        style={{ height: '100%', width: '100%' }}
        whenCreated={mapInstance => { window.map = mapInstance }}
        zoomControl={false}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <ZoomControl position="topright" />
        <ScaleControl position="bottomright" />
        <FeatureGroup>
          {isEditing && (
            <EditControl
              position="topright"
              onCreated={handleCreated}
              onEdited={handleEdited}
              draw={{
                rectangle: false,
                circle: false,
                circlemarker: false,
                marker: false,
                polyline: false,
                polygon: true
              }}
            />
          )}
          {zones.map((zone) => (
            <Polygon 
              key={zone.id} 
              positions={zone.coordinates}
              pathOptions={{ 
                color: selectedZone && selectedZone.id === zone.id ? 'blue' : 'red',
                fillColor: selectedZone && selectedZone.id === zone.id ? 'lightblue' : 'pink',
                fillOpacity: 0.3,
                weight: selectedZone && selectedZone.id === zone.id ? 3 : 2
              }}
              eventHandlers={{
                mouseover: (e) => {
                  const layer = e.target;
                  layer.setStyle({
                    fillOpacity: 0.7
                  });
                },
                mouseout: (e) => {
                  const layer = e.target;
                  layer.setStyle({
                    fillOpacity: 0.3
                  });
                },
                click: () => {
                  onZoneChange(zone);
                }
              }}
            >
              <Tooltip permanent direction="center" className="custom-tooltip">
                {zone.name}
              </Tooltip>
            </Polygon>
          ))}
        </FeatureGroup>
      </MapContainer>
    </div>
  );
};

export default ZoneMap;