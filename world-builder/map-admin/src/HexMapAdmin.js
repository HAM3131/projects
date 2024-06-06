import React, { useState, useEffect } from 'react';
import { HexGrid, Layout, Hexagon, Text, Pattern, Path, Hex } from 'react-hexgrid';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

const HexMapAdmin = () => {
  const [hexes, setHexes] = useState([]);

  useEffect(() => {
    axios.get('/api/hexes')
      .then(response => setHexes(response.data))
      .catch(error => console.error('Error fetching hex data:', error));
  }, []);

  return (
    <div>
      <HexGrid width={1200} height={800} viewBox="-50 -50 100 100">
        <Layout size={{ x: 10, y: 10 }} flat={true} spacing={1.02} origin={{ x: 0, y: 0 }}>
          {hexes.map(hex => (
            <Hexagon key={hex.id} q={hex.x} r={hex.y} s={-hex.x - hex.y}>
              <Text>{hex.x}, {hex.y}</Text>
            </Hexagon>
          ))}
        </Layout>
      </HexGrid>
    </div>
  );
};

export default HexMapAdmin;
