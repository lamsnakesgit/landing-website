/**
 * =============================================
 * WhatsApp РАССЫЛЬЩИК v1 — Google Apps Script + Evolution API
 * =============================================
 * 
 * ИНСТРУКЦИЯ:
 * 1. Создай Google Sheets таблицу с колонками: phone | name | company | status
 * 2. Заполни номера (любой формат: +7 999 123 45 67, 89991234567, 7999... — скрипт сам приведёт к формату WhatsApp)
 * 3. Открой: Расширения → Apps Script, вставь этот код
 * 4. Замени VPS_URL на реальный IP твоего ВПС
 * 5. Запусти функцию startSending()
 * 
 * ФОРМАТ ТАБЛИЦЫ (Google Sheets):
 * ┌─────────────────┬──────────────┬──────────────────┬─────────┐
 * │     phone       │    name      │    company       │ status  │
 * ├─────────────────┼──────────────┼──────────────────┼─────────┤
 * │ +7 999 123 4567 │ Анна         │ ООО "Логистик"   │         │
 * │ 89991234567     │ Иван         │ ИП Петров        │         │
 * │ 998901234567    │ Алишер       │ Cargo Express    │         │
 * └─────────────────┴──────────────┴──────────────────┴─────────┘
 * 
 * Колонка "status" заполняется АВТОМАТИЧЕСКИ: "✅ Отправлено" или "❌ Ошибка"
 */

// ========== НАСТРОЙКИ (ЗАМЕНИ!) ==========
const CONFIG = {
  // URL твоего ВПС (НЕ localhost!)
  // Найди IP в панели Hetzner/Railway/DigitalOcean
  VPS_URL: 'http://ВСТАВЬ_IP_ТВОЕГО_ВПС:8081',
  
  API_KEY: 'b5485840231d596018f5d67b50b4a05ffaaa792cec60595f',
  INSTANCE: '8326 301 n8n wa 1',
  
  // Безопасность
  MIN_DELAY_SEC: 10,  // Мин. пауза между сообщениями (секунды)
  MAX_DELAY_SEC: 20,  // Макс. пауза
  TYPING_DELAY: 3000, // Имитация набора текста (мс)
  
  // Имя листа в таблице
  SHEET_NAME: 'Лист1',
  
  // С какой строки начинать (2 = пропускаем заголовок)
  START_ROW: 2,
};

// ========== ШАБЛОН СООБЩЕНИЯ ==========
// Используй {name} и {company} — они подставятся автоматически
const MESSAGE_TEMPLATE = 
  'Здравствуйте, {name}!\n\n' +
  'Занимаемся перевозками грузов из Китая и Европы (авто, авиа, ж/д) от 15 тонн.\n\n' +
  'Если вашей компании {company} актуально — могу прислать актуальные тарифы?';


// ========== НОРМАЛИЗАЦИЯ НОМЕРОВ ==========

/**
 * Приводит ЛЮБОЙ формат номера к формату WhatsApp: 79991234567
 * Примеры:
 *   "+7 (999) 123-45-67" → "79991234567"
 *   "8-999-123-45-67"    → "79991234567"
 *   "89991234567"         → "79991234567"
 *   "998901234567"        → "998901234567" (Узбекистан, без изменений)
 *   "7999 123 4567"       → "79991234567"
 */
function normalizePhone(raw) {
  // Убираем всё кроме цифр
  let digits = raw.replace(/\D/g, '');
  
  // Если начинается с 8 и длина 11 → Россия, меняем 8 на 7
  if (digits.length === 11 && digits.startsWith('8')) {
    digits = '7' + digits.substring(1);
  }
  
  // Если начинается с + (уже убрали), проверяем длину
  // Для большинства стран номер 10-15 цифр
  if (digits.length < 10 || digits.length > 15) {
    return null; // Невалидный номер
  }
  
  return digits;
}


// ========== ОСНОВНОЙ КОД ==========

function startSending() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) {
    SpreadsheetApp.getUi().alert('Лист "' + CONFIG.SHEET_NAME + '" не найден!');
    return;
  }
  
  const lastRow = sheet.getLastRow();
  const data = sheet.getRange(CONFIG.START_ROW, 1, lastRow - 1, 4).getValues();
  // Колонки: [0]=phone, [1]=name, [2]=company, [3]=status
  
  let sent = 0;
  let errors = 0;
  
  for (let i = 0; i < data.length; i++) {
    const row = data[i];
    const rawPhone = String(row[0]).trim();
    const name = String(row[1]).trim() || '';
    const company = String(row[2]).trim() || '';
    const existingStatus = String(row[3]).trim();
    
    // Пропускаем уже отправленные
    if (existingStatus.includes('✅')) {
      continue;
    }
    
    // Нормализуем номер
    const phone = normalizePhone(rawPhone);
    if (!phone) {
      sheet.getRange(CONFIG.START_ROW + i, 4).setValue('❌ Неверный номер');
      errors++;
      continue;
    }
    
    // Подставляем переменные в шаблон
    let message = MESSAGE_TEMPLATE
      .replace(/\{name\}/gi, name || 'уважаемый клиент')
      .replace(/\{company\}/gi, company || 'вашей компании');
    
    Logger.log('Отправка на: ' + phone + ' (' + name + ')');
    
    try {
      // 1. Имитация набора текста
      sendPresence_(phone);
      Utilities.sleep(CONFIG.TYPING_DELAY);
      
      // 2. Отправка текста
      const result = sendText_(phone, message);
      
      if (result && !result.error) {
        sheet.getRange(CONFIG.START_ROW + i, 4).setValue('✅ Отправлено ' + new Date().toLocaleString());
        sent++;
      } else {
        sheet.getRange(CONFIG.START_ROW + i, 4).setValue('❌ Ошибка: ' + JSON.stringify(result));
        errors++;
      }
    } catch (e) {
      sheet.getRange(CONFIG.START_ROW + i, 4).setValue('❌ Сбой: ' + e.message);
      errors++;
    }
    
    // 3. Безопасная пауза
    if (i < data.length - 1) {
      const delaySec = Math.floor(Math.random() * (CONFIG.MAX_DELAY_SEC - CONFIG.MIN_DELAY_SEC) + CONFIG.MIN_DELAY_SEC);
      Logger.log('Пауза: ' + delaySec + ' сек...');
      Utilities.sleep(delaySec * 1000);
    }
  }
  
  // Итоговый отчёт
  SpreadsheetApp.getUi().alert(
    '🎉 Рассылка завершена!\n\n' +
    '✅ Отправлено: ' + sent + '\n' +
    '❌ Ошибок: ' + errors + '\n' +
    '📊 Всего строк: ' + data.length
  );
}


// ========== API ФУНКЦИИ ==========

function sendPresence_(number) {
  const url = CONFIG.VPS_URL + '/chat/sendPresence/' + encodeURIComponent(CONFIG.INSTANCE);
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'apikey': CONFIG.API_KEY },
    payload: JSON.stringify({
      number: number,
      presence: 'composing',
      delay: CONFIG.TYPING_DELAY
    }),
    muteHttpExceptions: true
  };
  
  try {
    UrlFetchApp.fetch(url, options);
  } catch (e) {
    Logger.log('Presence warning: ' + e.message);
  }
}

function sendText_(number, text) {
  const url = CONFIG.VPS_URL + '/message/sendText/' + encodeURIComponent(CONFIG.INSTANCE);
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'apikey': CONFIG.API_KEY },
    payload: JSON.stringify({
      number: number,
      text: text,
      delay: 1000
    }),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  return JSON.parse(response.getContentText());
}


// ========== МЕНЮ В GOOGLE SHEETS ==========
// Добавляет кнопку "🚀 Рассылка" в меню таблицы
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🚀 Рассылка')
    .addItem('▶️ Запустить рассылку', 'startSending')
    .addItem('📊 Тест одного номера', 'testSingleNumber')
    .addToUi();
}

// Тест отправки на первый номер в таблице
function testSingleNumber() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  const phone = normalizePhone(String(sheet.getRange(2, 1).getValue()));
  
  if (!phone) {
    SpreadsheetApp.getUi().alert('Неверный номер в ячейке A2!');
    return;
  }
  
  try {
    sendPresence_(phone);
    Utilities.sleep(2000);
    const result = sendText_(phone, 'Тест рассылки. Если видите это — всё работает! ✅');
    SpreadsheetApp.getUi().alert('Результат:\n' + JSON.stringify(result, null, 2));
  } catch (e) {
    SpreadsheetApp.getUi().alert('❌ Ошибка:\n' + e.message + '\n\nПроверь VPS_URL в CONFIG!');
  }
}
