const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
});

const PORT = process.env.PORT || 3000;
const DATA_DIR = path.join(__dirname, '..', 'данные');
const WEB_DIR = path.join(__dirname, '..', 'веб');
const SQUADS_FILE = path.join(DATA_DIR, 'база_сквадов.json');
const USERS_FILE = path.join(DATA_DIR, 'база_пользователей.json');
const MONGODB_URI = process.env.MONGODB_URI;

app.use(cors());
app.use(express.json());

// Health-check для UptimeRobot
app.get('/health', (req, res) => res.status(200).send('OK'));

// Публичный конфиг для клиента (Google Client ID)
app.get('/api/config', (req, res) => {
  res.json({
    googleClientId: process.env.GOOGLE_CLIENT_ID || ''
  });
});

// Статика веб-клиента
app.use(express.static(WEB_DIR, {
  setHeaders: (res, p) => {
    if (p.endsWith('.html') || p.endsWith('.js') || p.endsWith('.css') || p.endsWith('.json')) {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    }
  }
}));

// Маршруты для иконок маркеров
const ICONS_DIR = path.join(WEB_DIR, 'иконки');
app.use('/иконки', express.static(ICONS_DIR));
app.use('/icons', express.static(ICONS_DIR));

// Маршрут для старых спутниковых тайлов
const TILES_DIR = path.join(WEB_DIR, 'тайлы');
app.get('/tiles/:z/:x/:y', (req, res) => {
  const filePath = path.join(TILES_DIR, req.params.z, req.params.x, req.params.y);
  if (fs.existsSync(filePath)) {
    res.type('image/webp');
    return res.sendFile(filePath);
  }
  const oceanPath = path.join(TILES_DIR, '0', '0', '0.webp');
  if (fs.existsSync(oceanPath)) {
    res.type('image/webp');
    return res.sendFile(oceanPath);
  }
  res.status(404).end();
});

// ============================================================
//  ХЕШИРОВАНИЕ И ТОКЕНЫ
// ============================================================

function hashPassword(pass) {
  return crypto.createHash('sha256').update(String(pass).trim()).digest('hex');
}

function generateToken() {
  return crypto.randomBytes(32).toString('hex');
}

// ============================================================
//  БАЗА ДАННЫХ (DUAL-MODE: MongoDB Atlas + Failover JSON)
// ============================================================

let usersDb = {};   // { [userId]: { id, username, passwordHash, googleId, name, avatar, squadId, personalGarages, token, createdAt } }
let squadsDb = {};  // { [squadName]: { name, leaderId, passcode, members: [{ userId, name, avatar, role, joinedAt }], claims: {}, markers: [] } }

let User;
let Squad;
let useMongoDb = false;

// Загрузка начальных данных из локальных файлов
try {
  if (fs.existsSync(USERS_FILE)) usersDb = JSON.parse(fs.readFileSync(USERS_FILE, 'utf-8'));
} catch (e) { usersDb = {}; }

try {
  if (fs.existsSync(SQUADS_FILE)) squadsDb = JSON.parse(fs.readFileSync(SQUADS_FILE, 'utf-8'));
} catch (e) { squadsDb = {}; }

function saveLocalUsers() {
  try { fs.writeFileSync(USERS_FILE, JSON.stringify(usersDb, null, 2), 'utf-8'); }
  catch (e) { console.error('Ошибка записи USERS_FILE:', e); }
}

function saveLocalSquads() {
  try { fs.writeFileSync(SQUADS_FILE, JSON.stringify(squadsDb, null, 2), 'utf-8'); }
  catch (e) { console.error('Ошибка записи SQUADS_FILE:', e); }
}

async function syncUserToMongo(u) {
  if (useMongoDb && User && u) {
    try {
      await User.findOneAndUpdate(
        { id: u.id },
        { $set: u },
        { upsert: true, new: true }
      );
    } catch (e) { console.error('Ошибка записи User в Mongo:', e); }
  }
}

async function syncSquadToMongo(s) {
  if (useMongoDb && Squad && s) {
    try {
      await Squad.findOneAndUpdate(
        { name: s.name },
        { $set: s },
        { upsert: true, new: true }
      );
    } catch (e) { console.error('Ошибка записи Squad в Mongo:', e); }
  }
}

function persistUser(u) {
  saveLocalUsers();
  if (u) syncUserToMongo(u);
}

function persistSquad(s) {
  saveLocalSquads();
  if (s) syncSquadToMongo(s);
}

// Подключение к MongoDB Atlas
if (MONGODB_URI) {
  const mongoose = require('mongoose');

  const userSchema = new mongoose.Schema({
    id: { type: String, unique: true, required: true },
    username: { type: String, index: true },
    passwordHash: String,
    googleId: { type: String, index: true },
    name: String,
    avatar: String,
    squadId: String,
    personalGarages: { type: mongoose.Schema.Types.Mixed, default: {} },
    token: String,
    createdAt: { type: Date, default: Date.now }
  }, { strict: false, minimize: false });

  const squadSchema = new mongoose.Schema({
    name: { type: String, unique: true, required: true },
    leaderId: String,
    passcode: String,
    members: { type: [mongoose.Schema.Types.Mixed], default: [] },
    claims: { type: mongoose.Schema.Types.Mixed, default: {} },
    markers: { type: [mongoose.Schema.Types.Mixed], default: [] }
  }, { strict: false, minimize: false });

  User = mongoose.model('User', userSchema);
  Squad = mongoose.model('Squad', squadSchema);

  mongoose.connect(MONGODB_URI)
    .then(async () => {
      console.log('✅ MongoDB Atlas подключена');
      useMongoDb = true;

      // Синхронизация Users
      const allUsers = await User.find({});
      if (allUsers.length > 0) {
        for (const u of allUsers) {
          usersDb[u.id] = u.toObject();
        }
        console.log(`✅ Загружено пользователей из Mongo: ${allUsers.length}`);
      } else if (Object.keys(usersDb).length > 0) {
        for (const u of Object.values(usersDb)) await syncUserToMongo(u);
      }

      // Синхронизация Squads
      const allSquads = await Squad.find({});
      if (allSquads.length > 0) {
        for (const s of allSquads) {
          squadsDb[s.name] = s.toObject();
        }
        console.log(`✅ Загружено сквадов из Mongo: ${allSquads.length}`);
      } else if (Object.keys(squadsDb).length > 0) {
        for (const s of Object.values(squadsDb)) await syncSquadToMongo(s);
      }
    })
    .catch(err => {
      console.error('⚠️ Ошибка подключения к MongoDB:', err.message);
      console.log('📁 Работаем в надежном режиме локального JSON');
    });
}

// Middleware аутентификации
function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Необходима авторизация' });
  }
  const token = authHeader.split(' ')[1];
  const user = Object.values(usersDb).find(u => u.token === token);
  if (!user) {
    return res.status(401).json({ error: 'Сессия недействительна' });
  }
  req.user = user;
  next();
}

// ============================================================
//  API АВТОРИЗАЦИИ (РЕГИСТРАЦИЯ, ЛОГИН, GOOGLE)
// ============================================================

// 1. Регистрация по логину и паролю
app.post('/api/auth/register', (req, res) => {
  const { username, password, name } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Введите логин и пароль' });
  }

  const cleanUser = String(username).trim().toLowerCase();
  const exists = Object.values(usersDb).find(u => u.username === cleanUser);
  if (exists) {
    return res.status(400).json({ error: 'Пользователь с таким логином уже существует' });
  }

  const id = 'u_' + crypto.randomBytes(8).toString('hex');
  const token = generateToken();
  const newUser = {
    id,
    username: cleanUser,
    passwordHash: hashPassword(password),
    googleId: null,
    name: (name && String(name).trim()) || username,
    avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=' + cleanUser,
    squadId: null,
    personalGarages: {},
    token,
    createdAt: new Date().toISOString()
  };

  usersDb[id] = newUser;
  persistUser(newUser);

  res.json({ token, user: sanitizeUser(newUser) });
});

// 2. Вход по логину и паролю
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Введите логин и пароль' });
  }

  const cleanUser = String(username).trim().toLowerCase();
  const user = Object.values(usersDb).find(u => u.username === cleanUser);
  if (!user || user.passwordHash !== hashPassword(password)) {
    return res.status(401).json({ error: 'Неверный логин или пароль' });
  }

  user.token = generateToken();
  persistUser(user);

  res.json({ token: user.token, user: sanitizeUser(user) });
});

// 3. Вход через Google One Tap / GIS
app.post('/api/auth/google', (req, res) => {
  const { credential } = req.body;
  if (!credential) {
    return res.status(400).json({ error: 'Токен Google не передан' });
  }

  try {
    // Декодируем JWT payload от Google
    const parts = credential.split('.');
    if (parts.length !== 3) throw new Error('Некорректный JWT');
    const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString('utf-8'));

    const googleId = payload.sub;
    const email = payload.email || '';
    const name = payload.name || payload.given_name || 'Боец';
    const avatar = payload.picture || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + googleId;

    let user = Object.values(usersDb).find(u => u.googleId === googleId);
    if (!user) {
      // Новый пользователь Google
      const id = 'g_' + crypto.randomBytes(8).toString('hex');
      user = {
        id,
        username: null,
        passwordHash: null,
        googleId,
        email,
        name,
        avatar,
        squadId: null,
        personalGarages: {},
        token: generateToken(),
        createdAt: new Date().toISOString()
      };
      usersDb[id] = user;
    } else {
      user.name = name;
      user.avatar = avatar;
      user.token = generateToken();
    }

    persistUser(user);
    res.json({ token: user.token, user: sanitizeUser(user) });
  } catch (err) {
    console.error('Ошибка Google Auth:', err);
    res.status(400).json({ error: 'Ошибка верификации Google: ' + err.message });
  }
});

// 4. Проверка текущей сессии
app.get('/api/auth/me', authMiddleware, (req, res) => {
  res.json({ user: sanitizeUser(req.user) });
});

function sanitizeUser(u) {
  if (!u) return null;
  const { passwordHash, ...safe } = u;
  return safe;
}

// ============================================================
//  API ЛИЧНЫХ ГАРАЖЕЙ ОДИНОЧКИ
// ============================================================

// Сохранение личного гаража (когда игрок не в скваде)
app.post('/api/user/personal_claim', authMiddleware, (req, res) => {
  const { claim } = req.body;
  if (!claim || !claim.id) return res.status(400).json({ error: 'Некорректные данные' });

  req.user.personalGarages = req.user.personalGarages || {};
  req.user.personalGarages[claim.id] = {
    ...claim,
    owner: req.user.name,
    updatedAt: new Date().toISOString()
  };
  persistUser(req.user);

  res.json({ success: true, personalGarages: req.user.personalGarages });
});

// Удаление личного гаража
app.post('/api/user/delete_personal_claim', authMiddleware, (req, res) => {
  const { claimId } = req.body;
  if (!claimId) return res.status(400).json({ error: 'Не передан ID гаража' });

  if (req.user.personalGarages && req.user.personalGarages[claimId]) {
    delete req.user.personalGarages[claimId];
    persistUser(req.user);
  }

  res.json({ success: true, personalGarages: req.user.personalGarages });
});

// ============================================================
//  API УПРАВЛЕНИЯ СКВАДАМИ (СОЗДАНИЕ, ВСТУПЛЕНИЕ, КИК, ВЫХОД)
// ============================================================

// 1. Создание нового сквада
app.post('/api/squads/create', authMiddleware, (req, res) => {
  const { name, passcode } = req.body;
  const sName = String(name || '').trim();
  if (!sName) return res.status(400).json({ error: 'Введите название сквада' });

  if (squadsDb[sName]) {
    return res.status(400).json({ error: 'Сквад с таким названием уже существует' });
  }

  const newSquad = {
    name: sName,
    leaderId: req.user.id,
    passcode: passcode ? String(passcode).trim() : '',
    members: [{
      userId: req.user.id,
      name: req.user.name,
      avatar: req.user.avatar,
      role: 'leader',
      joinedAt: new Date().toISOString()
    }],
    claims: {},
    markers: []
  };

  squadsDb[sName] = newSquad;
  persistSquad(newSquad);

  req.user.squadId = sName;
  persistUser(req.user);

  res.json({ success: true, squad: newSquad, user: sanitizeUser(req.user) });
});

// 2. Вступление в сквад по паролю
app.post('/api/squads/join', authMiddleware, (req, res) => {
  const { name, passcode } = req.body;
  const sName = String(name || '').trim();
  const squad = squadsDb[sName];

  if (!squad) {
    return res.status(404).json({ error: 'Сквад не найден' });
  }

  if (squad.passcode && squad.passcode !== String(passcode || '').trim()) {
    return res.status(403).json({ error: 'Неверный пароль сквада' });
  }

  // Добавляем участника, если его еще нет
  if (!squad.members.some(m => m.userId === req.user.id)) {
    squad.members.push({
      userId: req.user.id,
      name: req.user.name,
      avatar: req.user.avatar,
      role: 'member',
      joinedAt: new Date().toISOString()
    });
    persistSquad(squad);
  }

  req.user.squadId = sName;
  persistUser(req.user);

  io.to(sName).emit('squad_members_updated', squad.members);
  res.json({ success: true, squad, user: sanitizeUser(req.user) });
});

// 3. Выход из сквада
app.post('/api/squads/leave', authMiddleware, (req, res) => {
  const sName = req.user.squadId;
  if (!sName || !squadsDb[sName]) {
    req.user.squadId = null;
    persistUser(req.user);
    return res.json({ success: true, user: sanitizeUser(req.user) });
  }

  const squad = squadsDb[sName];
  squad.members = squad.members.filter(m => m.userId !== req.user.id);

  // Если вышел лидер — передаем лидерство первому участнику или удаляем сквад
  if (squad.leaderId === req.user.id) {
    if (squad.members.length > 0) {
      squad.leaderId = squad.members[0].userId;
      squad.members[0].role = 'leader';
    } else {
      delete squadsDb[sName];
      if (useMongoDb && Squad) Squad.deleteOne({ name: sName }).catch(console.error);
    }
  }

  if (squadsDb[sName]) persistSquad(squad);

  req.user.squadId = null;
  persistUser(req.user);

  io.to(sName).emit('squad_members_updated', squad.members || []);
  res.json({ success: true, user: sanitizeUser(req.user) });
});

// 4. Кик участника (ТОЛЬКО ДЛЯ ЛИДЕРА)
app.post('/api/squads/kick', authMiddleware, (req, res) => {
  const { targetUserId } = req.body;
  const sName = req.user.squadId;
  const squad = squadsDb[sName];

  if (!squad) return res.status(404).json({ error: 'Сквад не найден' });
  if (squad.leaderId !== req.user.id) {
    return res.status(403).json({ error: 'Только командир может исключать участников' });
  }
  if (targetUserId === req.user.id) {
    return res.status(400).json({ error: 'Командир не может кикнуть сам себя' });
  }

  squad.members = squad.members.filter(m => m.userId !== targetUserId);
  persistSquad(squad);

  // Сбрасываем сквад у кикнутого пользователя
  if (usersDb[targetUserId]) {
    usersDb[targetUserId].squadId = null;
    persistUser(usersDb[targetUserId]);
  }

  // Оповещаем в реальном времени через Socket.io
  io.to(sName).emit('squad_members_updated', squad.members);
  io.emit('user_kicked_event', { userId: targetUserId, squadName: sName });

  res.json({ success: true, members: squad.members });
});

// 5. Смена пароля сквада (ТОЛЬКО ДЛЯ ЛИДЕРА)
app.post('/api/squads/passcode', authMiddleware, (req, res) => {
  const { newPasscode } = req.body;
  const sName = req.user.squadId;
  const squad = squadsDb[sName];

  if (!squad) return res.status(404).json({ error: 'Сквад не найден' });
  if (squad.leaderId !== req.user.id) {
    return res.status(403).json({ error: 'Только командир может менять пароль сквада' });
  }

  squad.passcode = String(newPasscode || '').trim();
  persistSquad(squad);

  res.json({ success: true, passcode: squad.passcode });
});

// ============================================================
//  API ДАННЫХ КАРТЫ
// ============================================================

app.get('/api/buildings', (req, res) => {
  const p = path.join(DATA_DIR, 'постройки_миссии.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

app.get('/api/island_buildings', (req, res) => {
  const p = path.join(DATA_DIR, 'дома_острова.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

app.get('/api/markers', (req, res) => {
  const p = path.join(DATA_DIR, 'маркеры_миссии.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

app.get('/api/cities', (req, res) => {
  const p = path.join(DATA_DIR, 'города.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

app.get('/api/roads', (req, res) => {
  const p = path.join(DATA_DIR, 'дороги.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

app.get('/api/territories', (req, res) => {
  const p = path.join(DATA_DIR, 'территории.json');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.json([]);
});

// ============================================================
//  SOCKET.IO — СИНХРОНИЗАЦИЯ В РЕАЛЬНОМ ВРЕМЕНИ
// ============================================================

const onlineUsersBySquad = {}; // { [squadName]: Set<userId> }

io.on('connection', (socket) => {
  let currentUser = null;
  let currentSquad = null;

  socket.on('auth_socket', ({ token }) => {
    if (!token) return;
    const user = Object.values(usersDb).find(u => u.token === token);
    if (!user) return;

    currentUser = user;
    currentSquad = user.squadId;

    if (currentSquad && squadsDb[currentSquad]) {
      socket.join(currentSquad);
      if (!onlineUsersBySquad[currentSquad]) onlineUsersBySquad[currentSquad] = new Set();
      onlineUsersBySquad[currentSquad].add(user.id);

      socket.emit('squad_data', squadsDb[currentSquad]);
      io.to(currentSquad).emit('squad_online', Array.from(onlineUsersBySquad[currentSquad]));
    } else {
      // Одиночка — отправляем личные гаражи
      socket.emit('personal_data', user.personalGarages || {});
    }
  });

  // Сохранение гаража (сквад или соло)
  socket.on('save_claim', ({ claim }) => {
    if (!currentUser || !claim || !claim.id) return;

    if (currentSquad && squadsDb[currentSquad]) {
      squadsDb[currentSquad].claims = squadsDb[currentSquad].claims || {};
      squadsDb[currentSquad].claims[claim.id] = {
        ...claim,
        owner: currentUser.name,
        updatedAt: new Date().toISOString()
      };
      persistSquad(squadsDb[currentSquad]);
      io.to(currentSquad).emit('claim_updated', squadsDb[currentSquad].claims[claim.id]);
    } else {
      // Сохраняем как личный
      currentUser.personalGarages = currentUser.personalGarages || {};
      currentUser.personalGarages[claim.id] = {
        ...claim,
        owner: currentUser.name,
        updatedAt: new Date().toISOString()
      };
      persistUser(currentUser);
      socket.emit('claim_updated', currentUser.personalGarages[claim.id]);
    }
  });

  // Удаление гаража
  socket.on('delete_claim', ({ claimId }) => {
    if (!currentUser || !claimId) return;

    if (currentSquad && squadsDb[currentSquad]) {
      if (squadsDb[currentSquad].claims && squadsDb[currentSquad].claims[claimId]) {
        delete squadsDb[currentSquad].claims[claimId];
        persistSquad(squadsDb[currentSquad]);
        io.to(currentSquad).emit('claim_removed', claimId);
      }
    } else {
      if (currentUser.personalGarages && currentUser.personalGarages[claimId]) {
        delete currentUser.personalGarages[claimId];
        persistUser(currentUser);
        socket.emit('claim_removed', claimId);
      }
    }
  });

  socket.on('disconnect', () => {
    if (currentUser && currentSquad && onlineUsersBySquad[currentSquad]) {
      onlineUsersBySquad[currentSquad].delete(currentUser.id);
      io.to(currentSquad).emit('squad_online', Array.from(onlineUsersBySquad[currentSquad]));
    }
  });
});

// ============================================================
//  ЗАПУСК СЕРВЕРА
// ============================================================

server.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(` Тактический сервер Arma 3 Altis успешно запущен!   `);
  console.log(` Порт: ${PORT} | Режим базы: ${useMongoDb ? 'MongoDB Atlas' : 'Локальный JSON'}`);
  console.log(`====================================================`);
});
