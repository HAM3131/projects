const express = require('express');
const cors = require('cors');
const mysql = require('mysql2');

const app = express();
app.use(cors());
app.use(express.json());

const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'password',
  database: 'dnd_world'
});

db.connect(err => {
  if (err) throw err;
  console.log('MySQL Connected...');
});

app.listen(5000, () => {
  console.log('Server started on port 5000');
});

