import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

const HexMap = () => {
  const [hexes, setHexes] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/api/hexes')
      .then(response => setHexes(response.data))
      .catch(error => console.error('Error fetching hex data:', error));
  }, []);

  return (
    <MapContainer center={[51.505, -0.09]} zoom={13} scrollWheelZoom={false}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {hexes.map(hex => (
        <Marker key={hex.id} position={[hex.x, hex.y]}>
          <Popup>
            {hex.history.map(entry => (
              <div key={entry.id}>
                <strong>Date:</strong> {entry.date}<br/>
                <strong>Entry:</strong> {entry.entry}
              </div>
            ))}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default HexMap;
