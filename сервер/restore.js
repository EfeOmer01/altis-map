const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const mongoose = require('mongoose');

const DEFAULT_MONGO_URI = 'mongodb+srv://efeomer311_db_user:xCDOhWuErezwGYA7@cluster0.zdeamq0.mongodb.net/altis_db?retryWrites=true&w=majority';
const MONGODB_URI = process.env.MONGODB_URI || DEFAULT_MONGO_URI;

const BACKUP_DIR = process.platform === 'win32'
  ? path.join(__dirname, '..', 'данные', 'backups')
  : '/var/backups/altis';

async function restoreBackup(targetFile) {
  let filePath = targetFile;
  if (!filePath || filePath === 'latest') {
    if (!fs.existsSync(BACKUP_DIR)) {
      throw new Error(`Директория бэкапов ${BACKUP_DIR} не найдена.`);
    }
    const files = fs.readdirSync(BACKUP_DIR)
      .filter(f => f.startsWith('altis_backup_') && f.endsWith('.json.gz'))
      .map(f => ({ name: f, path: path.join(BACKUP_DIR, f), time: fs.statSync(path.join(BACKUP_DIR, f)).mtimeMs }))
      .sort((a, b) => b.time - a.time);

    if (files.length === 0) {
      throw new Error(`В папке ${BACKUP_DIR} нет резервных копий.`);
    }
    filePath = files[0].path;
  } else if (!path.isAbsolute(filePath)) {
    filePath = path.join(BACKUP_DIR, filePath);
  }

  console.log(`[RESTORE] Восстановление из архива: ${filePath}`);
  const gzBuffer = fs.readFileSync(filePath);
  const jsonString = zlib.gunzipSync(gzBuffer).toString('utf8');
  const payload = JSON.parse(jsonString);

  console.log('[RESTORE] Метаданные копии:', payload.metadata);

  console.log('[RESTORE] Подключение к MongoDB Atlas...');
  await mongoose.connect(MONGODB_URI, { serverSelectionTimeoutMS: 10000 });

  const usersCol = mongoose.connection.collection('users');
  const squadsCol = mongoose.connection.collection('squads');

  const users = payload.mongodb?.users || [];
  const squads = payload.mongodb?.squads || [];

  if (users.length > 0) {
    for (const u of users) {
      const { _id, ...doc } = u;
      await usersCol.updateOne({ id: doc.id }, { $set: doc }, { upsert: true });
    }
    console.log(`[RESTORE] Восстановлено пользователей: ${users.length}`);
  }

  if (squads.length > 0) {
    for (const s of squads) {
      const { _id, ...doc } = s;
      await squadsCol.updateOne({ name: doc.name }, { $set: doc }, { upsert: true });
    }
    console.log(`[RESTORE] Восстановлено сквадов: ${squads.length}`);
  }

  await mongoose.disconnect();
  console.log('[RESTORE] База данных успешно восстановлена!');
}

if (require.main === module) {
  const target = process.argv[2] || 'latest';
  restoreBackup(target)
    .then(() => process.exit(0))
    .catch(err => {
      console.error('[RESTORE] Ошибка восстановления:', err);
      process.exit(1);
    });
}

module.exports = { restoreBackup };
