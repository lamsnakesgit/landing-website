/**
 * WhatsApp Рассыльщик v1 — Evolution API + Google Sheets
 * 
 * Читает номера и сообщения из Google Sheets,
 * отправляет через Evolution API с безопасными задержками.
 * 
 * ИСПОЛЬЗОВАНИЕ:
 * 1. Заполни переменные CONFIG ниже (API ключ, URL, инстанс)
 * 2. Создай Google Sheet и опубликуй как CSV (Файл → Опубликовать → CSV)
 * 3. Запусти: node evolution_sender.js
 */

const https = require('https');
const http = require('http');

// ========== НАСТРОЙКИ (ЗАПОЛНИ!) ==========
const CONFIG = {
  // Evolution API
  apiKey: 'ВСТАВЬ_СЮДА_API_KEY',
  serverUrl: 'ВСТАВЬ_СЮДА_URL', // например: http://localhost:8081
  instanceName: 'ВСТАВЬ_СЮДА_ИМЯ_ИНСТАНСА',
  
  // Google Sheets (опубликуй таблицу как CSV)
  // Файл → Поделиться → Опубликовать в интернете → CSV
  googleSheetCsvUrl: 'ВСТАВЬ_ССЫЛКУ_НА_CSV',
  
  // Безопасность
  minDelay: 8000,  // Мин. задержка между сообщениями (мс)
  maxDelay: 15000, // Макс. задержка
  typingDelay: 3000, // Имитация набора текста (мс)
};

// ========== СООБЩЕНИЕ ==========
// Используй {name} и {company} для подстановки из таблицы
const MESSAGE_TEMPLATE = `Здравствуйте, {name}!

Занимаемся перевозками грузов из Китая и Европы (авто, авиа, ж/д) от 15 тонн.

Если вам актуально — могу прислать актуальные тарифы?`;

// ========== КОД (НЕ ТРОГАЙ) ==========

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const randomDelay = () => Math.floor(Math.random() * (CONFIG.maxDelay - CONFIG.minDelay) + CONFIG.minDelay);

async function fetchGoogleSheet() {
  console.log('📊 Загрузка данных из Google Sheets...');
  
  return new Promise((resolve, reject) => {
    const fetcher = CONFIG.googleSheetCsvUrl.startsWith('https') ? https : http;
    fetcher.get(CONFIG.googleSheetCsvUrl, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const lines = data.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        
        const contacts = lines.slice(1).map(line => {
          const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
          const obj = {};
          headers.forEach((h, i) => obj[h] = values[i] || '');
          return obj;
        }).filter(c => {
          // Ищем поле с номером телефона
          const phone = c.phone || c.number || c.номер || c.телефон || '';
          return phone.replace(/\D/g, '').length > 5;
        });
        
        console.log(`✅ Загружено контактов: ${contacts.length}`);
        resolve(contacts);
      });
      res.on('error', reject);
    });
  });
}

function prepareMessage(template, contact) {
  let msg = template;
  // Подставляем все поля из таблицы
  Object.keys(contact).forEach(key => {
    msg = msg.replace(new RegExp(`{${key}}`, 'gi'), contact[key]);
  });
  // Убираем незаполненные плейсхолдеры
  msg = msg.replace(/\{[^}]+\}/g, '');
  return msg;
}

function getPhoneNumber(contact) {
  const raw = contact.phone || contact.number || contact.номер || contact.телефон || '';
  return raw.replace(/\D/g, '');
}

async function sendPresence(number) {
  const url = `${CONFIG.serverUrl}/chat/sendPresence/${encodeURIComponent(CONFIG.instanceName)}`;
  const body = JSON.stringify({
    number: number,
    presence: 'composing',
    delay: CONFIG.typingDelay
  });

  return new Promise((resolve) => {
    const fetcher = url.startsWith('https') ? https : http;
    const parsed = new URL(url);
    const req = fetcher.request({
      hostname: parsed.hostname,
      port: parsed.port,
      path: parsed.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': CONFIG.apiKey
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', () => resolve(null));
    req.write(body);
    req.end();
  });
}

async function sendTextMessage(number, text) {
  const url = `${CONFIG.serverUrl}/message/sendText/${encodeURIComponent(CONFIG.instanceName)}`;
  const body = JSON.stringify({
    number: number,
    text: text,
    delay: 1000
  });

  return new Promise((resolve, reject) => {
    const fetcher = url.startsWith('https') ? https : http;
    const parsed = new URL(url);
    const req = fetcher.request({
      hostname: parsed.hostname,
      port: parsed.port,
      path: parsed.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': CONFIG.apiKey
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch {
          resolve(data);
        }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function run() {
  console.log('🚀 WhatsApp Рассыльщик v1 (Evolution API + Google Sheets)');
  console.log('='.repeat(55));

  // Проверка настроек
  if (CONFIG.apiKey.includes('ВСТАВЬ') || CONFIG.serverUrl.includes('ВСТАВЬ')) {
    console.log('\n❌ ОШИБКА: Заполни CONFIG в начале файла!');
    console.log('   - apiKey: API ключ Evolution API');
    console.log('   - serverUrl: URL сервера (например http://localhost:8081)');
    console.log('   - instanceName: Имя инстанса WhatsApp');
    console.log('   - googleSheetCsvUrl: Ссылка на CSV таблицы');
    process.exit(1);
  }

  const contacts = await fetchGoogleSheet();
  
  if (contacts.length === 0) {
    console.log('❌ Контакты не найдены. Проверь ссылку на Google Sheet.');
    process.exit(1);
  }

  let success = 0;
  let failed = 0;

  for (let i = 0; i < contacts.length; i++) {
    const contact = contacts[i];
    const phone = getPhoneNumber(contact);
    const message = prepareMessage(MESSAGE_TEMPLATE, contact);
    
    console.log(`\n[${i + 1}/${contacts.length}] 📱 ${phone}`);
    console.log(`   Имя: ${contact.name || contact.имя || 'Н/Д'}`);

    try {
      // 1. Имитация набора
      console.log('   ⌨️ Печатаем...');
      await sendPresence(phone);
      await sleep(CONFIG.typingDelay);

      // 2. Отправка
      const result = await sendTextMessage(phone, message);
      
      if (result && !result.error) {
        console.log('   ✅ Отправлено!');
        success++;
      } else {
        console.log(`   ❌ Ошибка: ${JSON.stringify(result)}`);
        failed++;
      }
    } catch (e) {
      console.log(`   ❌ Сбой: ${e.message}`);
      failed++;
    }

    // 3. Безопасная пауза
    if (i < contacts.length - 1) {
      const delay = randomDelay();
      console.log(`   ⏳ Пауза ${Math.round(delay / 1000)} сек...`);
      await sleep(delay);
    }
  }

  console.log('\n' + '='.repeat(55));
  console.log(`🎉 ГОТОВО! Отправлено: ${success} | Ошибок: ${failed} | Всего: ${contacts.length}`);
}

run().catch(console.error);
