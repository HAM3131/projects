const express = require('express');
const cors = require('cors');
const mariadb = require('mariadb');
const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');

const app = express();
const httpPort = 8080;
const httpsPort = 8443;
app.use(cors());
app.use(express.json());

const httpsOptions = {
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.crt')
};

const pool = mariadb.createPool({
  host: '127.0.0.1',
  user: 'dnd_server',
  password: '1234',
  database: 'dnd_world',
  connectionLimit: 5
});

// Create HTTP server
http.createServer(app).listen(httpPort, () => {
  console.log(`HTTP Server started on port ${httpPort}`);
});

// Create HTTPS server
https.createServer(httpsOptions, app).listen(httpsPort, () => {
  console.log(`HTTPS Server started on port ${httpsPort}`);
});

/*
-------------------------- API GET REQUESTS ---------------------------
*/

app.get('/api/hexes', async (req, res) => {
  let conn;
  try {
    conn = await pool.getConnection();
    const rows = await conn.query(
     `SELECT ht.*
      FROM hex_tiles ht
      JOIN dates d ON ht.date_id = d.id
      JOIN (
          SELECT x_value, y_value, MAX(d.id) as max_date_id
          FROM hex_tiles ht
          JOIN dates d ON ht.date_id = d.id
          WHERE d.order < 5
          GROUP BY x_value, y_value
      ) subquery ON ht.x_value = subquery.x_value AND ht.y_value = subquery.y_value AND ht.date_id = subquery.max_date_id;
     `);
    res.json(rows);
  } catch (err) {
    throw err;
  } finally {
    if (conn) conn.end();
  }
});

app.get('/api/dates', async (req, res) => {
  let conn;
  try {
    conn = await pool.getConnection();
    const rows = await conn.query(
     `SELECT * FROM dates
     `);
    res.json(rows);
  } catch (err) {
    throw err;
  } finally {
    if (conn) conn.end();
  }
});

app.get('/api/history', async (req, res) => {
  let conn;
  try {
    conn = await pool.getConnection();
    const rows = await conn.query(
     `SELECT h.*, d.value as date_value, d.order as date_order FROM history h
      JOIN dates d ON h.date = d.id 
      WHERE x = ${req.query['hex-x']} 
      AND y = ${req.query['hex-y']} 
      AND d.order < ${req.query['date']}
      ORDER BY d.order DESC
     `);
    res.json(rows)
  } catch (err) {
    console.log(err);
  } finally {
    if (conn) conn.end();
  }
});

/*
-------------------------- API PUT REQUESTS ---------------------------
*/
app.put('/api/history', async (req, res) => {
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


/*
-------------------------- STATIC FILES ---------------------------
*/

// Serve static files for user and admin interfaces
app.use('/map', express.static(path.join(__dirname, 'public/map')));
app.use('/map-admin', express.static(path.join(__dirname, 'public/map-admin')));

// Serve /map/ if no path is provided
app.get('/', (req, res) => {
  res.redirect('/map/');
});

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