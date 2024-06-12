import React, { useState, useEffect } from 'react';
import { HexGrid, Layout, Hexagon, Text } from 'react-hexgrid';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import axios from 'axios';
import './App.css';

const HexMap = () => {
  const [hexes, setHexes] = useState([]);
  const [history, setHistory] = useState(null);
  const [selectedHex, setSelectedHex] = useState(null);
  var date = 2; // Set default date to the earliest possible value

  useEffect(() => {
    axios.get(`/api/hexes?date=${date}`)
      .then(response => setHexes(response.data))
      .catch(error => console.error('Error fetching hex data:', error));
  }, []);

  const fetchHistory = (hex) => {
    axios.get(`/api/history?hex-x=${hex.x}&hex-y=${hex.y}&date=${hex.date_id}`)
      .then(response => {
        setHistory(response.data);
        setSelectedHex({ "id": hex.id, "x": hex.x, "y": hex.y , "name": hex.name});
        document.getElementById('history-element').scrollIntoView({ behavior: 'smooth' });
      })
      .catch(error => console.error('Error fetching history data:', error));
  };

  const groupByDateValue = (history) => {
    const grouped = {};
    history.forEach(event => {
      if (!grouped[event.date_value]) {
        grouped[event.date_value] = {
          entries: [],
          date_id: event.date,
          date_order: event.date_order
        };
      }
      grouped[event.date_value].entries.push(event);
    });
    return grouped;
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
                          onClick={() => fetchHistory(hex)}
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
            <h2>History of {selectedHex['name']}</h2>
            <div>
              {Object.entries(groupByDateValue(history)).map(([date_value, group]) => (
                <div key={date_value} className="history-date-group">
                  <div className="date-value"
                    title={`Date ID: ${group.date_id}, Order: ${group.date_order}`}>{date_value}</div>
                  <div className="history-entries">
                    {group.entries.map(event => (
                      <div key={event.id} className="history-entry">
                        <h3>{event.title}</h3>
                        <p>{event.entry}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p>Select a hex to view its history.</p>
        )}
      </div>
    </div>
  );
};

export default HexMap;
