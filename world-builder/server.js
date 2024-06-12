const express = require('express');
const cors = require('cors');
const mariadb = require('mariadb');
const multer = require('multer');
const fs = require('fs');
const fsp = require('fs').promises;
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

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadPath = path.join(__dirname, 'public/icons');
    // Ensure the directory exists
    fs.mkdir(uploadPath, { recursive: true }, (err) => {
      if (err) {
        return cb(err);
      }
      cb(null, uploadPath);
    });
  },
  filename: function (req, file, cb) {
    const iconFilename = req.body.iconPath || file.originalname;
    cb(null, iconFilename);
  }
});

const upload = multer({ storage: storage });

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
          SELECT x, y, MAX(d.id) as max_date_id
          FROM hex_tiles ht
          JOIN dates d ON ht.date_id = d.id
          WHERE d.order < ${req.query['date']}
          GROUP BY x, y
      ) subquery ON ht.x = subquery.x AND ht.y = subquery.y AND ht.date_id = subquery.max_date_id;
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
// New route to insert or update a hex tile
app.put('/api/hexes/set', async (req, res) => {
  const { x, y, date } = req.body;
  const icon = req.body.icon || null;
  const tags = req.body.tags || null;
  const name = req.body.name || null;
  try {
    const conn = await pool.getConnection();
    const query = `
      INSERT INTO hex_tiles (x, y, date_id, icon, tags, name)
      VALUES (?, ?, ?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE
      icon = VALUES(icon),
      tags = VALUES(tags),
      name = VALUES(name)
    `;
    await conn.query(query, [x, y, date, icon, tags, name]);
    conn.release();
    res.status(200).send('Hex tile inserted or updated successfully.');
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// New route to remove a hex tile
app.put('/api/hexes/remove', async (req, res) => {
  const { x, y, date } = req.body;
  try {
    const conn = await pool.getConnection();
    const query = `
      DELETE FROM hex_tiles
      WHERE x = ?
      AND y = ?
      AND date_id = ?
    `;
    await conn.query(query, [x, y, date]);
    conn.release();
    res.status(200).send('Hex tile removed successfully.');
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// New route to handle icon uploads
app.put('/api/icon/set', upload.single('iconFile'), async (req, res) => {
  const { icon_name, icon_path } = req.body;
  const iconFile = req.file;

  if (!icon_name || !icon_path || !iconFile) {
    return res.status(400).send('Icon name, path, and file are required.');
  }

  try {
    const conn = await pool.getConnection();
    const query = `
      INSERT INTO icons (name, path)
      VALUES (?, ?)
      ON DUPLICATE KEY UPDATE
      path = VALUES(path)
    `;
    await conn.query(query, [icon_name, icon_path]);
    conn.release();
    res.status(200).send('Icon uploaded successfully.');
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// New route to handle icon removal
app.put('/api/icon/remove', async (req, res) => {
  const { icon_name } = req.body;
  let icon_path;

  try {
    const conn = await pool.getConnection();
    const query = `
      SELECT path FROM icons
      WHERE name = ?
    `;
    const rows = await conn.query(query, [icon_name]);
    
    if (rows.length > 0) {
      icon_path = rows[0].path;
    } else {
      conn.release();
      return res.status(404).send('Icon not found');
    }

    const query2 = `
      DELETE FROM icons
      WHERE name = ?
    `;
    await conn.query(query2, [icon_name]);
    conn.release();

    // Remove the file
    await fsp.rm(`public/icons/${icon_path}`);
    res.status(200).send('Icon removed successfully');
  } catch (err) {
    res.status(500).send(err.message);
  }
});

/*
-------------------------- STATIC FILES ---------------------------
*/

// Middleware and routes
app.use(express.static(path.join(__dirname, 'public')));
// Serve static files for user and admin interfaces
app.use('/map', express.static(path.join(__dirname, 'public/map')));
app.use('/map-admin', express.static(path.join(__dirname, 'public/map-admin')));

// Serve /map/ if no path is provided
app.get('/', (req, res) => {
  res.redirect('/map/');
});

// Serve the appropriate index.html for the /map route
app.get('/map', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/map', 'index.html'));
});

// Serve the appropriate index.html for the /map-admin route
app.get('/map-admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/map-admin', 'index.html'));
});

// Default catch-all route to handle other routes (if needed)
app.get('*', (req, res) => {
  res.status(404).send('Not Found');
});
