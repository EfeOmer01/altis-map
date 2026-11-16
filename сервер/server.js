const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
});

const PORT = process.env.PORT || 3000;
const DATA_DIR = path.join(__dirname, '..', 'данные');
const WEB_DIR = path.join(__dirname, '..', 'веб');
const DB_FILE = path.join(DATA_DIR, 'база_сквадов.json');

app.use(cors());
app.use(express.json());

// Статика веб-клиента с отключением кэша для свежих стилей и скриптов
app.use(express.static(WEB_DIR, {
  setHeaders: (res, p) => {
    if (p.endsWith('.html') || p.endsWith('.js') || p.endsWith('.css') || p.endsWith('.json')) {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    }
  }
}));

// Маршрут для иконок маркеров
const ICONS_DIR = path.join(WEB_DIR, 'иконки');
app.use('/иконки', express.static(ICONS_DIR));
app.use('/icons', express.static(ICONS_DIR));

// Маршрут для тайлов карты (с бесшовной отдачей океана за пределами суши)
const TILES_DIR = path.join(WEB_DIR, 'тайлы');
app.get('/tiles/:z/:x/:y', (req, res) => {
  const filePath = path.join(TILES_DIR, req.params.z, req.params.x, req.params.y);
  if (fs.existsSync(filePath)) {
    res.type('image/webp');
    return res.sendFile(filePath);
  }
  // Если тайл в океане или за краем — отдаем чистый океанский тайл
  const oceanPath = path.join(TILES_DIR, '0', '0', '0.webp');
  if (fs.existsSync(oceanPath)) {
    res.type('image/webp');
    return res.sendFile(oceanPath);
  }
  res.status(404).end();
});

// База данных сквадов
let squadsDb = {};
if (fs.existsSync(DB_FILE)) {
  try {
    squadsDb = JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
  } catch (e) {
    squadsDb = {};
  }
}

function saveDb() {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(squadsDb, null, 2), 'utf-8');
  } catch (e) {
    console.error('Ошибка записи базы сквадов:', e);
  }
}

// 1. API интерактивных объектов (гаражи миссии)
app.get('/api/buildings', (req, res) => {
  const p = path.join(DATA_DIR, 'постройки_миссии.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

// 1.1 API всех домов и построек острова (12,843 здания с карты)
app.get('/api/island_buildings', (req, res) => {
  const p = path.join(DATA_DIR, 'дома_острова.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

// 2. API маркеров/иконок миссии
app.get('/api/markers', (req, res) => {
  const p = path.join(DATA_DIR, 'маркеры_миссии.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

// 3. API городов и населенных пунктов
app.get('/api/cities', (req, res) => {
  const p = path.join(DATA_DIR, 'города.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

// 4. API дорожной сети
app.get('/api/roads', (req, res) => {
  const p = path.join(DATA_DIR, 'дороги.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

// 5. API территорий и зон (сейфзоны, радиация, охота)
app.get('/api/territories', (req, res) => {
  const p = path.join(DATA_DIR, 'территории.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

// Socket.io для синхронизации сквадов
const squadOnline = {};

io.on('connection', (socket) => {
  let currentSquad = null;
  let currentNick = null;

  socket.on('join_squad', ({ squad, nick }) => {
    if (currentSquad && squadOnline[currentSquad]) {
      squadOnline[currentSquad].delete(currentNick);
      io.to(currentSquad).emit('squad_members', Array.from(squadOnline[currentSquad]));
      socket.leave(currentSquad);
    }

    currentSquad = squad || 'ОДИНОЧНЫЙ';
    currentNick = nick || 'Боец';
    socket.join(currentSquad);

    if (!squadOnline[currentSquad]) {
      squadOnline[currentSquad] = new Set();
    }
    squadOnline[currentSquad].add(currentNick);

    if (!squadsDb[currentSquad]) {
      squadsDb[currentSquad] = { name: currentSquad, claims: {}, markers: [] };
      saveDb();
    }

    socket.emit('squad_data', squadsDb[currentSquad]);
    io.to(currentSquad).emit('squad_members', Array.from(squadOnline[currentSquad]));
  });

  socket.on('save_claim', ({ squad, claim }) => {
    const sName = squad || currentSquad;
    if (!sName || !claim || !claim.id) return;

    if (!squadsDb[sName]) squadsDb[sName] = { name: sName, claims: {}, markers: [] };
    squadsDb[sName].claims[claim.id] = claim;
    saveDb();
    io.to(sName).emit('claim_updated', claim);
  });

  socket.on('delete_claim', ({ squad, claimId }) => {
    const sName = squad || currentSquad;
    if (!sName || !claimId) return;

    if (squadsDb[sName] && squadsDb[sName].claims[claimId]) {
      delete squadsDb[sName].claims[claimId];
      saveDb();
      io.to(sName).emit('claim_removed', claimId);
    }
  });

  socket.on('disconnect', () => {
    if (currentSquad && currentNick && squadOnline[currentSquad]) {
      squadOnline[currentSquad].delete(currentNick);
      io.to(currentSquad).emit('squad_members', Array.from(squadOnline[currentSquad]));
    }
  });
});

server.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(` Тактический сервер Arma 3 Altis успешно запущен!   `);
  console.log(` Адрес в браузере: http://localhost:${PORT}          `);
  console.log(`====================================================`);
});
