const express = require('express');
const cors = require('cors');
const mariadb = require('mariadb');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const pool = mariadb.createPool({
  host: '127.0.0.1',
  user: 'dnd_server',
  password: '1234',
  database: 'dnd_world',
  connectionLimit: 5
});

app.listen(5000, () => {
  console.log('Server started on port 5000');
});

app.get('/api/hexes', async (req, res) => {
  let conn;
  try {
    conn = await pool.getConnection();
    const rows = await conn.query('SELECT * FROM hex_tiles');
    res.json(rows);
  } catch (err) {
    throw err;
  } finally {
    if (conn) conn.end();
  }
});

app.put('/api/hexes/:id', async (req, res) => {
  const { id } = req.params;
  const { history } = req.body;
  let conn;
  try {
    conn = await pool.getConnection();
    await conn.query('UPDATE hex_tiles SET history = ? WHERE id = ?', [history, id]);
    res.json({ id, history });
  } catch (err) {
    throw err;
  } finally {
    if (conn) conn.end();
  }
});

// Serve static files for user and admin interfaces
app.use('/map', express.static(path.join(__dirname, 'public/map')));
app.use('/map-admin', express.static(path.join(__dirname, 'public/map-admin')));

// Serve the appropriate index.html for the /map route
app.get('/map/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/map', 'index.html'));
});

// Serve the appropriate index.html for the /map-admin route
app.get('/map-admin/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/map-admin', 'index.html'));
});

// Default catch-all route to handle other routes (if needed)
app.get('*', (req, res) => {
  res.status(404).send('Not Found');
});