import React, { useState, useEffect } from 'react';
import { HexGrid, Layout, Hexagon, Text } from 'react-hexgrid';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import axios from 'axios';
import './App.css';

const HexMap = () => {
  const [hexes, setHexes] = useState([]);
  const [history, setHistory] = useState(null);
  const [selectedHex, setSelectedHex] = useState(null);

  useEffect(() => {
    axios.get('/api/hexes')
      .then(response => setHexes(response.data))
      .catch(error => console.error('Error fetching hex data:', error));
  }, []);

  const fetchHistory = (hex_x, hex_y, hexId) => {
    axios.get(`/api/history?hex-x=${hex_x}&hex-y=${hex_y}`)
      .then(response => {
        setHistory(response.data);
        setSelectedHex(hexId);
        document.getElementById('history-element').scrollIntoView({ behavior: 'smooth' });
      })
      .catch(error => console.error('Error fetching history data:', error));
  };

  return (
    <div>
      <div className="map-container">
        <TransformWrapper
          initialScale={0.5}
          minScale={0.2}
          maxScale={4}
          wheel={{ disabled: true }}
          centerOnInit={true}
          limitToBounds={false}
          limitToWrapper={false}
          pan={{
            paddingSize: 0, // Disable padding when panning
          }}
          >
          {({ zoomIn, zoomOut, centerView }) => (
            <>
              <div className="tools">
                <button onClick={() => zoomIn()}>Zoom In</button>
                <button onClick={() => zoomOut()}>Zoom Out</button>
                <button onClick={() => centerView(0.5)}>Reset</button> {/* Reset and center */}
              </div>
              <div className="hexgrid-container">
                <TransformComponent>
                  <HexGrid width={2000} height={1200} viewBox="-50 -50 100 100">
                    <Layout size={{ x: 10, y: 10 }} flat={true} spacing={1} origin={{ x: 0, y: 0 }}>
                      {hexes.map(hex => (
                        <Hexagon 
                        key={hex.id} 
                          q={hex.x} 
                          r={hex.y} 
                          s={-hex.x - hex.y}
                          onClick={() => fetchHistory(hex.x, hex.y, hex.id)}
                          >
                          <Text>{hex.x}, {hex.y}</Text>
                        </Hexagon>
                      ))}
                    </Layout>
                  </HexGrid>
                </TransformComponent>
              </div>
            </>
          )}
        </TransformWrapper>
      </div>
      <div id="history-element" className="history-element">
        {history ? (
          <>
            <h2>History for Hex {selectedHex}</h2>
            <ul>
              {history.map(entry => (
                <li key={entry.id}>
                  <strong>{entry.date}:</strong> {entry.entry}
                </li>
              ))}
            </ul>
          </>
        ) : (
          <p>Select a hex to view its history.</p>
        )}
      </div>
    </div>
  );
};

export default HexMap;
