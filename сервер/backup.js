const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const mongoose = require('mongoose');

const DEFAULT_MONGO_URI = 'mongodb+srv://efeomer311_db_user:xCDOhWuErezwGYA7@cluster0.zdeamq0.mongodb.net/altis_db?retryWrites=true&w=majority';
const MONGODB_URI = process.env.MONGODB_URI || DEFAULT_MONGO_URI;

// Директория для хранения резервных копий
const BACKUP_DIR = process.platform === 'win32'
  ? path.join(__dirname, '..', 'данные', 'backups')
  : '/var/backups/altis';

const LOCAL_DATA_DIR = path.join(__dirname, '..', 'данные');
const MAX_BACKUPS = 8; // Хранить последние 8 еженедельных копий (2 месяца)

async function createBackup() {
  const startTime = Date.now();
  const dateStr = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  console.log(`[BACKUP] Запуск резервного копирования: ${new Date().toLocaleString('ru-RU')}`);

  if (!fs.existsSync(BACKUP_DIR)) {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
    console.log(`[BACKUP] Создана папка для бэкапов: ${BACKUP_DIR}`);
  }

  let mongoData = { users: [], squads: [] };
  let mongoConnected = false;

  try {
    console.log('[BACKUP] Подключение к MongoDB Atlas...');
    await mongoose.connect(MONGODB_URI, { serverSelectionTimeoutMS: 10000 });
    mongoConnected = true;

    const usersCol = mongoose.connection.collection('users');
    const squadsCol = mongoose.connection.collection('squads');

    const users = await usersCol.find({}).toArray();
    const squads = await squadsCol.find({}).toArray();

    mongoData.users = users;
    mongoData.squads = squads;

    console.log(`[BACKUP] Успешно выгружено из MongoDB Atlas: пользователей: ${users.length}, сквадов: ${squads.length}`);
    await mongoose.disconnect();
  } catch (err) {
    console.error('[BACKUP] Ошибка подключения к MongoDB Atlas:', err.message);
  }

  // Также считываем локальные резервные JSON файлы, если они есть
  let localUsers = null;
  let localSquads = null;
  try {
    const uPath = path.join(LOCAL_DATA_DIR, 'база_пользователей.json');
    const sPath = path.join(LOCAL_DATA_DIR, 'база_сквадов.json');
    if (fs.existsSync(uPath)) localUsers = JSON.parse(fs.readFileSync(uPath, 'utf8'));
    if (fs.existsSync(sPath)) localSquads = JSON.parse(fs.readFileSync(sPath, 'utf8'));
  } catch (err) {
    console.warn('[BACKUP] Предупреждение при чтении локальных файлов:', err.message);
  }

  // Считаем общую статистику
  let totalClaims = 0;
  let totalLogs = 0;
  (mongoData.squads || []).forEach(s => {
    if (s.claims) totalClaims += Object.keys(s.claims).length;
    if (s.logs) totalLogs += s.logs.length;
  });

  const backupPayload = {
    metadata: {
      createdAt: new Date().toISOString(),
      mongoConnected,
      usersCount: mongoData.users.length,
      squadsCount: mongoData.squads.length,
      totalClaimsCount: totalClaims,
      totalLogsCount: totalLogs,
      environment: process.env.NODE_ENV || 'production'
    },
    mongodb: mongoData,
    localFallback: {
      users: localUsers,
      squads: localSquads
    }
  };

  const jsonString = JSON.stringify(backupPayload, null, 2);
  const compressedBuffer = zlib.gzipSync(Buffer.from(jsonString, 'utf8'));

  const backupFileName = `altis_backup_${dateStr}.json.gz`;
  const backupFilePath = path.join(BACKUP_DIR, backupFileName);

  fs.writeFileSync(backupFilePath, compressedBuffer);
  const fileSizeKb = (compressedBuffer.length / 1024).toFixed(1);

  console.log(`[BACKUP] Резервная копия успешно создана!`);
  console.log(`[BACKUP] Файл: ${backupFilePath} (${fileSizeKb} KB)`);
  console.log(`[BACKUP] Затрачено времени: ${((Date.now() - startTime) / 1000).toFixed(2)} сек.`);

  // Очистка старых резервных копий (ротация)
  try {
    const files = fs.readdirSync(BACKUP_DIR)
      .filter(f => f.startsWith('altis_backup_') && f.endsWith('.json.gz'))
      .map(f => ({ name: f, path: path.join(BACKUP_DIR, f), time: fs.statSync(path.join(BACKUP_DIR, f)).mtimeMs }))
      .sort((a, b) => b.time - a.time);

    if (files.length > MAX_BACKUPS) {
      const toDelete = files.slice(MAX_BACKUPS);
      toDelete.forEach(f => {
        fs.unlinkSync(f.path);
        console.log(`[BACKUP] Удалена старая резервная копия: ${f.name}`);
      });
    }
  } catch (err) {
    console.error('[BACKUP] Ошибка при ротации старых копий:', err.message);
  }

  return {
    success: true,
    file: backupFileName,
    path: backupFilePath,
    sizeKb: fileSizeKb,
    metadata: backupPayload.metadata
  };
}

if (require.main === module) {
  createBackup()
    .then(() => process.exit(0))
    .catch(err => {
      console.error('[BACKUP] Фатальная ошибка резервного копирования:', err);
      process.exit(1);
    });
}

module.exports = { createBackup };
