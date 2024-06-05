import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

const HexMapAdmin = () => {
  const [hexes, setHexes] = useState([]);
  const [selectedHex, setSelectedHex] = useState(null);
  const [date, setDate] = useState('');
  const [entry, setEntry] = useState('');

  useEffect(() => {
    axios.get('http://localhost:5000/api/hexes')
      .then(response => setHexes(response.data))
      .catch(error => console.error('Error fetching hex data:', error));
  }, []);

  const handleSave = () => {
    if (selectedHex) {
      axios.post('http://localhost:5000/api/history', { hex: selectedHex.id, date, entry })
        .then(response => {
          const newHistory = [...selectedHex.history, response.data];
          setHexes(hexes.map(hex => hex.id === selectedHex.id ? { ...hex, history: newHistory } : hex));
          setSelectedHex(null);
          setDate('');
          setEntry('');
        })
        .catch(error => console.error('Error adding history:', error));
    }
  };

  return (
    <div>
      <MapContainer center={[51.505, -0.09]} zoom={13} scrollWheelZoom={false}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {hexes.map(hex => (
          <Marker key={hex.id} position={[hex.x, hex.y]} eventHandlers={{
            click: () => {
              setSelectedHex(hex);
            },
          }}>
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
      {selectedHex && (
        <div>
          <h2>Add History for Hex ({selectedHex.x}, {selectedHex.y})</h2>
          <input type="text" placeholder="Date" value={date} onChange={e => setDate(e.target.value)} />
          <textarea placeholder="Entry" value={entry} onChange={e => setEntry(e.target.value)} />
          <button onClick={handleSave}>Save</button>
        </div>
      )}
    </div>
  );
};

export default HexMapAdmin;
