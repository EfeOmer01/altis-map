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
const DEFAULT_MONGO_URI = 'mongodb+srv://efeomer311_db_user:xCDOhWuErezwGYA7@cluster0.zdeamq0.mongodb.net/altis_db?retryWrites=true&w=majority';
let MONGODB_URI = process.env.MONGODB_URI || DEFAULT_MONGO_URI;
// Если в Render задана старая переменная с опечаткой (zdcamq0 вместо zdeamq0), исправляем на правильный URI
if (MONGODB_URI.includes('zdcamq0')) {
  MONGODB_URI = DEFAULT_MONGO_URI;
}

let mongoError = null;

app.use(cors());
app.use(express.json());

// Health-check для UptimeRobot
app.get('/health', (req, res) => res.status(200).send('OK'));

// Публичный конфиг для клиента
app.get('/api/config', (req, res) => {
  res.json({
    googleClientId: process.env.GOOGLE_CLIENT_ID || '',
    mongoConnected: useMongoDb,
    mongoError: mongoError,
    mongoHost: MONGODB_URI ? (MONGODB_URI.split('@')[1] || '').split('?')[0] : 'none',
    usersCount: Object.keys(usersDb).length,
    squadsCount: Object.keys(squadsDb).length
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

function cleanupTargetSquad(targetRegex) {
  let changed = false;
  for (const name of Object.keys(squadsDb)) {
    if (targetRegex.test(name.trim())) {
      console.log(`🗑️ Удаление сквада: ${name}`);
      delete squadsDb[name];
      changed = true;
    }
  }
  for (const u of Object.values(usersDb)) {
    if (u.squadId && targetRegex.test(u.squadId.trim())) {
      console.log(`👤 Сброс сквада у пользователя: ${u.name || u.id}`);
      u.squadId = null;
      changed = true;
    }
  }
  if (changed) {
    saveLocalSquads();
    saveLocalUsers();
  }
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
    joinRequests: { type: [mongoose.Schema.Types.Mixed], default: [] },
    claims: { type: mongoose.Schema.Types.Mixed, default: {} },
    markers: { type: [mongoose.Schema.Types.Mixed], default: [] }
  }, { strict: false, minimize: false });

  User = mongoose.model('User', userSchema);
  Squad = mongoose.model('Squad', squadSchema);

  mongoose.connect(MONGODB_URI, { serverSelectionTimeoutMS: 8000 })
    .then(async () => {
      console.log('✅ MongoDB Atlas подключена');
      useMongoDb = true;
      mongoError = null;

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
      mongoError = err.message;
      useMongoDb = false;
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
    // Если пользователь уже есть и пароль верный — просто выполняем вход!
    if (exists.passwordHash === hashPassword(password)) {
      exists.token = generateToken();
      persistUser(exists);
      return res.json({ token: exists.token, user: sanitizeUser(exists) });
    }
    return res.status(400).json({ error: 'Пользователь с таким логином уже существует. Введите верный пароль.' });
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

// 2. Вход по логину и паролю (с авто-созданием аккаунта в облачной базе MongoDB)
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Введите логин и пароль' });
  }

  const cleanUser = String(username).trim().toLowerCase();
  let user = Object.values(usersDb).find(u => u.username === cleanUser);

  // Если пользователя еще нет в MongoDB Atlas:
  // Автоматически регистрируем его прямо сейчас, чтобы никогда не было ошибки "аккаунт потерян"!
  if (!user) {
    const id = 'u_' + crypto.randomBytes(8).toString('hex');
    const token = generateToken();
    user = {
      id,
      username: cleanUser,
      passwordHash: hashPassword(password),
      googleId: null,
      name: String(username).trim(),
      avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=' + cleanUser,
      squadId: null,
      personalGarages: {},
      token,
      createdAt: new Date().toISOString()
    };
    usersDb[id] = user;
    persistUser(user);
    console.log(`✅ Пользователь "${cleanUser}" автоматически зарегистрирован в MongoDB Atlas и авторизован.`);
    return res.json({ token: user.token, user: sanitizeUser(user) });
  }

  // Если пользователь уже существует — проверяем пароль
  if (user.passwordHash !== hashPassword(password)) {
    return res.status(401).json({ error: 'Неверный пароль' });
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

  const assignedOwner = (claim.owner !== undefined && String(claim.owner).trim() !== '')
    ? String(claim.owner).trim()
    : (req.user.name || 'Боец');

  req.user.personalGarages = req.user.personalGarages || {};
  req.user.personalGarages[claim.id] = {
    ...claim,
    owner: assignedOwner,
    updatedBy: req.user.name || 'Боец',
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
    joinRequests: [],
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

function isSquadAdminOrLeader(squad, userId) {
  if (!squad || !userId) return false;
  if (squad.leaderId === userId) return true;
  return (squad.members || []).some(m => m.userId === userId && (m.role === 'admin' || m.role === 'leader'));
}

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

// 4.1. Изменение роли участника (Повышение до админа / понижение до бойца - ТОЛЬКО ДЛЯ ЛИДЕРА)
app.post('/api/squads/set_role', authMiddleware, (req, res) => {
  const { targetUserId, newRole } = req.body;
  const sName = req.user.squadId;
  const squad = squadsDb[sName];

  if (!squad) return res.status(404).json({ error: 'Сквад не найден' });
  if (squad.leaderId !== req.user.id) {
    return res.status(403).json({ error: 'Только командир сквада может назначать администраторов' });
  }
  if (!['admin', 'member'].includes(newRole)) {
    return res.status(400).json({ error: 'Недопустимая роль. Допустимы: admin, member' });
  }
  if (targetUserId === req.user.id) {
    return res.status(400).json({ error: 'Нельзя изменить роль создателя (командира) сквада' });
  }

  const member = (squad.members || []).find(m => m.userId === targetUserId);
  if (!member) {
    return res.status(404).json({ error: 'Участник не найден в составе сквада' });
  }

  member.role = newRole;
  persistSquad(squad);

  // Оповещаем сокет-комнату сквада в реальном времени
  io.to(sName).emit('squad_members_updated', squad.members);

  res.json({ success: true, member, members: squad.members });
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

// 5.1. Массовая смена паролей на дружественных гаражах (ТОЛЬКО ДЛЯ АДМИНОВ И КОМАНДИРА)
app.post('/api/squads/bulk_password', authMiddleware, (req, res) => {
  const { newPassword } = req.body;
  const sName = req.user.squadId;
  const cleanPass = String(newPassword !== undefined ? newPassword : '').trim();

  if (sName && squadsDb[sName]) {
    const squad = squadsDb[sName];

    // Проверка прав: только админы и лидер
    if (!isSquadAdminOrLeader(squad, req.user.id)) {
      return res.status(403).json({ error: 'Только администраторы и командир сквада могут массово менять пароли' });
    }

    squad.claims = squad.claims || {};
    let count = 0;

    Object.keys(squad.claims).forEach(id => {
      const c = squad.claims[id];
      if (c && (c.status === 'friendly' || !c.status)) {
        c.password = cleanPass;
        c.updatedBy = req.user.name || 'Админ';
        c.updatedAt = new Date().toISOString();
        count++;
      }
    });

    persistSquad(squad);
    io.to(sName).emit('squad_claims_all_updated', squad.claims);
    return res.json({ success: true, count, claims: squad.claims });
  } else {
    req.user.personalGarages = req.user.personalGarages || {};
    let count = 0;

    Object.keys(req.user.personalGarages).forEach(id => {
      const c = req.user.personalGarages[id];
      if (c && (c.status === 'friendly' || !c.status)) {
        c.password = cleanPass;
        c.updatedBy = req.user.name || 'Боец';
        c.updatedAt = new Date().toISOString();
        count++;
      }
    });

    persistUser(req.user);
    return res.json({ success: true, count, claims: req.user.personalGarages });
  }
});

// 6. Роспуск / удаление сквада (ТОЛЬКО ДЛЯ ЛИДЕРА)
app.post('/api/squads/disband', authMiddleware, async (req, res) => {
  const sName = req.user.squadId;
  const squad = squadsDb[sName];

  if (!squad) return res.status(404).json({ error: 'Сквад не найден' });
  if (squad.leaderId !== req.user.id) {
    return res.status(403).json({ error: 'Только командир может распустить сквад' });
  }

  // Сбрасываем squadId у всех участников сквада
  for (const m of (squad.members || [])) {
    if (usersDb[m.userId]) {
      usersDb[m.userId].squadId = null;
      persistUser(usersDb[m.userId]);
    }
  }
  req.user.squadId = null;
  persistUser(req.user);

  // Удаляем сквад из squadsDb и локального файла
  delete squadsDb[sName];
  saveLocalSquads();

  if (useMongoDb && Squad) {
    try {
      await Squad.deleteOne({ name: sName });
    } catch (e) {
      console.error('Ошибка удаления Squad из Mongo:', e);
    }
  }

  // Оповещаем участников через сокет
  io.to(sName).emit('squad_disbanded', { squadName: sName });

  res.json({ success: true, message: 'Сквад успешно распущен' });
});

// Экстренный эндпоинт очистки сквада ENOT / енот
app.get('/api/squads/purge_enot', async (req, res) => {
  cleanupTargetSquad(/^(enot|енот)$/i);
  if (useMongoDb && Squad) {
    try {
      await Squad.deleteMany({ name: { $regex: /^(enot|енот)$/i } });
    } catch (e) {}
  }
  res.json({ success: true, message: 'Сквад енот/ENOT удален из всех баз' });
});

// 7. Подача заявки на вступление по ссылке
app.post('/api/squads/request_join', authMiddleware, (req, res) => {
  const { squadName } = req.body;
  const sName = String(squadName || '').trim();
  const squad = squadsDb[sName];

  if (!squad) return res.status(404).json({ error: 'Сквад не найден' });
  if (req.user.squadId === sName) {
    return res.status(400).json({ error: 'Вы уже состоите в этом скваде' });
  }

  squad.joinRequests = squad.joinRequests || [];
  const existingReq = squad.joinRequests.find(r => r.userId === req.user.id);
  if (existingReq) {
    return res.status(400).json({ error: 'Вы уже отправили заявку в этот сквад. Ожидайте решения командира.' });
  }

  const newReq = {
    userId: req.user.id,
    name: req.user.name,
    avatar: req.user.avatar,
    requestedAt: new Date().toISOString()
  };
  squad.joinRequests.push(newReq);
  persistSquad(squad);

  // Оповещаем сокет-комнату сквада в реальном времени
  io.to(sName).emit('squad_requests_updated', squad.joinRequests);

  res.json({ success: true, message: `Заявка в сквад "${sName}" успешно отправлена командиру!` });
});

// 8. Принятие заявки (ТОЛЬКО ДЛЯ ЛИДЕРА)
app.post('/api/squads/accept_request', authMiddleware, async (req, res) => {
  const { targetUserId } = req.body;
  const sName = req.user.squadId;
  const squad = squadsDb[sName];

  if (!squad) return res.status(404).json({ error: 'Сквад не найден' });
  if (squad.leaderId !== req.user.id) {
    return res.status(403).json({ error: 'Только командир может принимать заявки' });
  }

  let targetUser = usersDb[targetUserId];
  if (!targetUser && mongoConnected) {
    const doc = await User.findOne({ id: targetUserId });
    if (doc) {
      targetUser = doc.toObject();
      usersDb[targetUserId] = targetUser;
    }
  }

  squad.joinRequests = (squad.joinRequests || []).filter(r => r.userId !== targetUserId);

  if (!targetUser) {
    persistSquad(squad);
    return res.status(404).json({ error: 'Пользователь не найден' });
  }

  squad.members = squad.members || [];
  if (!squad.members.some(m => m.userId === targetUserId)) {
    squad.members.push({
      userId: targetUser.id,
      name: targetUser.name,
      avatar: targetUser.avatar,
      role: 'member',
      joinedAt: new Date().toISOString()
    });
  }

  targetUser.squadId = sName;
  persistUser(targetUser);
  persistSquad(squad);

  io.to(sName).emit('squad_members_updated', squad.members);
  io.to(sName).emit('squad_requests_updated', squad.joinRequests);
  io.emit('user_request_accepted_event', { userId: targetUserId, squadName: sName });

  res.json({ success: true, squad });
});

// 9. Отклонение заявки (ТОЛЬКО ДЛЯ ЛИДЕРА)
app.post('/api/squads/reject_request', authMiddleware, (req, res) => {
  const { targetUserId } = req.body;
  const sName = req.user.squadId;
  const squad = squadsDb[sName];

  if (!squad) return res.status(404).json({ error: 'Сквад не найден' });
  if (squad.leaderId !== req.user.id) {
    return res.status(403).json({ error: 'Только командир может отклонять заявки' });
  }

  squad.joinRequests = (squad.joinRequests || []).filter(r => r.userId !== targetUserId);
  persistSquad(squad);

  io.to(sName).emit('squad_requests_updated', squad.joinRequests);
  io.emit('user_request_rejected_event', { userId: targetUserId, squadName: sName });

  res.json({ success: true, joinRequests: squad.joinRequests });
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

    socket.join('user_' + user.id);

    if (currentSquad && squadsDb[currentSquad]) {
      socket.join(currentSquad);
      if (!onlineUsersBySquad[currentSquad]) onlineUsersBySquad[currentSquad] = new Set();
      onlineUsersBySquad[currentSquad].add(user.id);

      socket.emit('squad_data', squadsDb[currentSquad]);
      if (squadsDb[currentSquad].leaderId === user.id) {
        socket.emit('squad_requests_updated', squadsDb[currentSquad].joinRequests || []);
      }
      io.to(currentSquad).emit('squad_online', Array.from(onlineUsersBySquad[currentSquad]));
    } else {
      // Одиночка — отправляем личные гаражи
      socket.emit('personal_data', user.personalGarages || {});
    }
  });

  // Сохранение гаража (сквад или соло)
  socket.on('save_claim', ({ claim }) => {
    if (!currentUser || !claim || !claim.id) return;

    const assignedOwner = (claim.owner !== undefined && String(claim.owner).trim() !== '')
      ? String(claim.owner).trim()
      : (currentUser.name || 'Боец');

    if (currentSquad && squadsDb[currentSquad]) {
      squadsDb[currentSquad].claims = squadsDb[currentSquad].claims || {};
      squadsDb[currentSquad].claims[claim.id] = {
        ...claim,
        owner: assignedOwner,
        updatedBy: currentUser.name || 'Боец',
        updatedAt: new Date().toISOString()
      };
      persistSquad(squadsDb[currentSquad]);
      io.to(currentSquad).emit('claim_updated', squadsDb[currentSquad].claims[claim.id]);
    } else {
      // Сохраняем как личный
      currentUser.personalGarages = currentUser.personalGarages || {};
      currentUser.personalGarages[claim.id] = {
        ...claim,
        owner: assignedOwner,
        updatedBy: currentUser.name || 'Боец',
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

  // Массовая смена паролей на дружественных гаражах
  socket.on('bulk_update_friendly_passwords', ({ newPassword }, callback) => {
    if (!currentUser) {
      if (typeof callback === 'function') callback({ success: false, error: 'Необходима авторизация' });
      return;
    }
    const cleanPass = String(newPassword !== undefined ? newPassword : '').trim();
    let count = 0;

    if (currentSquad && squadsDb[currentSquad]) {
      const squad = squadsDb[currentSquad];
      squad.claims = squad.claims || {};
      Object.keys(squad.claims).forEach(id => {
        const c = squad.claims[id];
        if (c && (c.status === 'friendly' || !c.status)) {
          c.password = cleanPass;
          c.updatedBy = currentUser.name || 'Боец';
          c.updatedAt = new Date().toISOString();
          count++;
        }
      });
      persistSquad(squad);
      io.to(currentSquad).emit('squad_claims_all_updated', squad.claims);
      if (typeof callback === 'function') callback({ success: true, count, claims: squad.claims });
    } else {
      currentUser.personalGarages = currentUser.personalGarages || {};
      Object.keys(currentUser.personalGarages).forEach(id => {
        const c = currentUser.personalGarages[id];
        if (c && (c.status === 'friendly' || !c.status)) {
          c.password = cleanPass;
          c.updatedBy = currentUser.name || 'Боец';
          c.updatedAt = new Date().toISOString();
          count++;
        }
      });
      persistUser(currentUser);
      socket.emit('squad_claims_all_updated', currentUser.personalGarages);
      if (typeof callback === 'function') callback({ success: true, count, claims: currentUser.personalGarages });
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
