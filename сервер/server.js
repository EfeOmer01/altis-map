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
const MONGODB_URI = process.env.MONGODB_URI;

app.use(cors());
app.use(express.json());

// Health-check для UptimeRobot (не даёт бесплатному Render уснуть)
app.get('/health', (req, res) => res.status(200).send('OK'));

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

// ============================================================
//  БАЗА ДАННЫХ СКВАДОВ (двойной режим: MongoDB / локальный файл)
// ============================================================

let squadsDb = {};     // Кэш в оперативной памяти (для быстрого Socket.io)
let Squad;             // Mongoose-модель (только при подключённой MongoDB)
let useMongoDb = false;

// Загружаем начальное состояние из локального JSON (если есть)
if (fs.existsSync(DB_FILE)) {
  try { squadsDb = JSON.parse(fs.readFileSync(DB_FILE, 'utf-8')); } catch (e) { squadsDb = {}; }
}

// Сохранение в локальный файл (только в режиме без MongoDB)
function saveToFile() {
  if (!useMongoDb) {
    try { fs.writeFileSync(DB_FILE, JSON.stringify(squadsDb, null, 2), 'utf-8'); }
    catch (e) { console.error('Ошибка записи базы сквадов:', e); }
  }
}

// Сохранение в MongoDB (асинхронно, не блокирует Socket.io)
async function saveToMongo(squadName) {
  if (useMongoDb && Squad && squadsDb[squadName]) {
    try {
      await Squad.findOneAndUpdate(
        { name: squadName },
        { $set: { claims: squadsDb[squadName].claims || {}, markers: squadsDb[squadName].markers || [] } },
        { upsert: true, new: true }
      );
    } catch (e) { console.error('Ошибка записи в MongoDB:', e); }
  }
}

// Единая функция сохранения: пишет и в файл (если нет Mongo), и в Mongo (если есть)
function saveDb(squadName) {
  saveToFile();
  if (squadName) saveToMongo(squadName);
}

// Подключение к MongoDB Atlas (если задана переменная окружения MONGODB_URI)
if (MONGODB_URI) {
  const mongoose = require('mongoose');

  const squadSchema = new mongoose.Schema({
    name: { type: String, unique: true, required: true },
    claims: { type: mongoose.Schema.Types.Mixed, default: {} },
    markers: { type: [mongoose.Schema.Types.Mixed], default: [] }
  }, { strict: false, minimize: false });

  Squad = mongoose.model('Squad', squadSchema);

  mongoose.connect(MONGODB_URI)
    .then(async () => {
      console.log('✅ MongoDB Atlas подключена');
      useMongoDb = true;

      // Загружаем все сквады из MongoDB в оперативную память
      const allSquads = await Squad.find({});
      if (allSquads.length > 0) {
        squadsDb = {};
        for (const s of allSquads) {
          squadsDb[s.name] = { name: s.name, claims: s.claims || {}, markers: s.markers || [] };
        }
        console.log(`✅ Загружено ${allSquads.length} сквадов из MongoDB`);
      } else if (Object.keys(squadsDb).length > 0) {
        // Первый запуск: автоматическая миграция данных из JSON в MongoDB
        console.log('📦 Миграция данных из JSON в MongoDB...');
        for (const [name, data] of Object.entries(squadsDb)) {
          await Squad.findOneAndUpdate(
            { name },
            { $set: { claims: data.claims || {}, markers: data.markers || [] } },
            { upsert: true }
          );
        }
        console.log('✅ Миграция завершена');
      }
    })
    .catch(err => {
      console.error('❌ Ошибка подключения к MongoDB:', err.message);
      console.log('⚠️  Работаем в режиме локального файла');
    });
}

// ============================================================
//  API ДАННЫХ КАРТЫ
// ============================================================

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

// ============================================================
//  SOCKET.IO — СИНХРОНИЗАЦИЯ СКВАДОВ В РЕАЛЬНОМ ВРЕМЕНИ
// ============================================================

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
      saveDb(currentSquad);
    }

    socket.emit('squad_data', squadsDb[currentSquad]);
    io.to(currentSquad).emit('squad_members', Array.from(squadOnline[currentSquad]));
  });

  socket.on('save_claim', ({ squad, claim }) => {
    const sName = squad || currentSquad;
    if (!sName || !claim || !claim.id) return;

    if (!squadsDb[sName]) squadsDb[sName] = { name: sName, claims: {}, markers: [] };
    squadsDb[sName].claims[claim.id] = claim;
    saveDb(sName);
    io.to(sName).emit('claim_updated', claim);
  });

  socket.on('delete_claim', ({ squad, claimId }) => {
    const sName = squad || currentSquad;
    if (!sName || !claimId) return;

    if (squadsDb[sName] && squadsDb[sName].claims[claimId]) {
      delete squadsDb[sName].claims[claimId];
      saveDb(sName);
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

// ============================================================
//  ЗАПУСК СЕРВЕРА
// ============================================================

server.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(` Тактический сервер Arma 3 Altis успешно запущен!   `);
  console.log(` Адрес в браузере: http://localhost:${PORT}          `);
  console.log(` Режим базы: ${MONGODB_URI ? 'MongoDB Atlas ☁️' : 'Локальный файл 💾'}`);
  console.log(`====================================================`);
});
