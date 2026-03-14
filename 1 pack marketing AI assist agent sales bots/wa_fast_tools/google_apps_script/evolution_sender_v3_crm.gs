/**
 * WhatsApp Рассыльщик v3 — CRM + Spintax + Follow-up
 * 
 * СТРУКТУРА ТАБЛИЦЫ (создаётся автоматически через "📋 Создать CRM"):
 * A=phone | B=name | C=company | D=status | E=tag | F=segment | G=pipeline | H=notes | I=last_sent
 * 
 * ТЕГИ (колонка E): можно несколько через запятую: "клиент, партнёр"
 * СТАТУСЫ (D): отправить | отправлено ✅ | дожим | ответил | пропустить | ошибка ❌
 * PIPELINE (G): новый → отправлено → ответил → КП отправлено → сделка → отказ
 * SEGMENT (F): рассылки | ии-бот | автоматизация | всё
 */

// === НАСТРОЙКИ ===
var SERVER_URL = "https://evolutionapi.aiconicvibe.store";
var API_KEY = "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f";
var INSTANCE = "8326 301 n8n wa 1";

// === КОЛОНКИ ===
var COL = { PHONE: 1, NAME: 2, COMPANY: 3, STATUS: 4, TAG: 5, SEGMENT: 6, PIPELINE: 7, NOTES: 8, LAST_SENT: 9, MEDIA: 10 };


// ==========================================
// SPINTAX — Рандомизация текста
// ==========================================
function spintax(text) {
  return text.replace(/\{([^}]+)\}/g, function(match, group) {
    var options = group.split('|');
    return options[Math.floor(Math.random() * options.length)];
  });
}

// Шаблон с рандомизацией. {вариант1|вариант2|вариант3} — выберет один случайный
var MESSAGE_FIRST = 
  "{Привет|Здравствуйте|Добрый день}, {name}!\n\n" +
  "{Привожу клиентов для бизнеса без вложений в рекламу|Помогаю бизнесу получать клиентов — без рекламы и холодных звонков|Нахожу клиентов для бизнеса без бюджета на рекламу}.\n\n" +
  "{Мои клиенты получают заявки уже в первую неделю|Первые заявки приходят уже на первой неделе} — без Яндекс.Директа, без таргета, без SEO.\n\n" +
  "{Интересно узнать как? Просто ответьте на это сообщение|Актуально? Ответьте — расскажу подробнее|Было бы интересно? Напишите «да» — скину детали}";

var MESSAGE_FOLLOWUP =
  "{Привет|Здравствуйте}, {name}! {Писал вам ранее|Отправлял сообщение пару дней назад}.\n\n" +
  "{Может быть сейчас актуальнее?|Вдруг всё-таки интересно?} {Могу скинуть короткий кейс|Могу показать как это работает на примере}.\n\n" +
  "{Просто ответьте и я расскажу подробнее|Напишите «да» если интересно}";


// ==========================================
// ОСНОВНАЯ РАССЫЛКА
// ==========================================
function sendWhatsAppMessages() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0, errors = 0, skipped = 0;

  for (var i = 2; i <= lastRow; i++) {
    var rawPhone = String(sheet.getRange(i, COL.PHONE).getValue()).trim();
    var name = String(sheet.getRange(i, COL.NAME).getValue()).trim();
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim();

    // Отправляем только "отправить"
    if (status !== "отправить") { skipped++; continue; }
    if (!rawPhone || rawPhone.length < 5) continue;

    var phone = normalizePhone(rawPhone);
    if (!phone) { sheet.getRange(i, COL.STATUS).setValue("ошибка ❌"); errors++; continue; }

    // Spintax: каждое сообщение уникальное
    var message = spintax(MESSAGE_FIRST).replace(/\{name\}/g, name || "");
    var mediaUrl = String(sheet.getRange(i, COL.MEDIA).getValue()).trim();

    var success = false;
    if (mediaUrl && mediaUrl.length > 5) {
      // Если есть ссылка на медиа - отправляем медиа с подписью
      success = sendMedia(phone, message, mediaUrl);
    } else {
      // Иначе обычный текст
      success = sendText(phone, message);
    }
    
    if (success) {
      sheet.getRange(i, COL.STATUS).setValue("отправлено ✅");
      sheet.getRange(i, COL.PIPELINE).setValue("отправлено");
      sheet.getRange(i, COL.LAST_SENT).setValue(new Date().toLocaleString());
      sent++;
    } else {
      sheet.getRange(i, COL.STATUS).setValue("ошибка ❌");
      errors++;
    }

    Utilities.sleep(8000 + Math.floor(Math.random() * 7000)); // 8-15 сек рандомная пауза
  }

  Logger.log("РАССЫЛКА: ✅ " + sent + " | ❌ " + errors + " | ⏭ " + skipped);
}


// ==========================================
// ДОЖИМ (Follow-up для молчунов)
// ==========================================
function sendFollowUp() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0, skipped = 0;

  for (var i = 2; i <= lastRow; i++) {
    var rawPhone = String(sheet.getRange(i, COL.PHONE).getValue()).trim();
    var name = String(sheet.getRange(i, COL.NAME).getValue()).trim();
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim();

    // Дожимаем только тех кто "отправлено ✅" (не ответили)
    if (status !== "отправлено ✅") { skipped++; continue; }

    var phone = normalizePhone(rawPhone);
    if (!phone) continue;

    var message = spintax(MESSAGE_FOLLOWUP).replace(/\{name\}/g, name || "");

    var success = sendText(phone, message);
    
    if (success) {
      sheet.getRange(i, COL.STATUS).setValue("дожим");
      sheet.getRange(i, COL.LAST_SENT).setValue(new Date().toLocaleString());
      sent++;
    }

    Utilities.sleep(10000 + Math.floor(Math.random() * 10000)); // 10-20 сек
  }

  Logger.log("ДОЖИМ: ✅ " + sent + " | ⏭ " + skipped);
}


// ==========================================
// РАССЫЛКА ПО ТЕГУ
// ==========================================
function sendByTag() {
  var ui = SpreadsheetApp.getUi();
  var result = ui.prompt('Введите тег для рассылки', 'Например: клиент', ui.ButtonSet.OK_CANCEL);
  if (result.getSelectedButton() !== ui.Button.OK) return;
  
  var targetTag = result.getResponseText().trim().toLowerCase();
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0;

  for (var i = 2; i <= lastRow; i++) {
    var tags = String(sheet.getRange(i, COL.TAG).getValue()).toLowerCase();
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim();
    
    // Проверяем что тег совпадает (поддержка нескольких через запятую)
    if (tags.indexOf(targetTag) === -1) continue;
    if (status !== "отправить") continue;

    var rawPhone = String(sheet.getRange(i, COL.PHONE).getValue()).trim();
    var name = String(sheet.getRange(i, COL.NAME).getValue()).trim();
    var phone = normalizePhone(rawPhone);
    if (!phone) continue;

    var message = spintax(MESSAGE_FIRST).replace(/\{name\}/g, name || "");
    
    if (sendText(phone, message)) {
      sheet.getRange(i, COL.STATUS).setValue("отправлено ✅");
      sheet.getRange(i, COL.LAST_SENT).setValue(new Date().toLocaleString());
      sent++;
    }

    Utilities.sleep(10000 + Math.floor(Math.random() * 5000));
  }

  Logger.log("ПО ТЕГУ [" + targetTag + "]: ✅ " + sent);
}


// ==========================================
// СОЗДАТЬ CRM-ШАБЛОН ТАБЛИЦЫ
// ==========================================
function createCRMTemplate() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  // Заголовки
  var headers = [["📱 Телефон", "👤 Имя", "🏢 Компания", "📊 Статус", "🏷 Теги", "🎯 Сегмент", "📈 Воронка", "📝 Заметки", "🕐 Последняя отправка", "🖼 Ссылка на Картинку (URL)"]];
  sheet.getRange(1, 1, 1, 10).setValues(headers);
  sheet.getRange(1, 1, 1, 10).setFontWeight("bold").setBackground("#1a73e8").setFontColor("white");

  // Примеры
  var examples = [
    ["+7 999 123 4567", "Анна", "ООО Логистик", "отправить", "клиент", "рассылки", "новый", "", "", "https://i.imgur.com/example.jpg"],
    ["89991234567", "Иван", "ИП Петров", "отправить", "клиент, партнёр", "ии-бот", "новый", "Знакомый по конференции", "", ""],
    ["8 705 739 6014", "Валерий", "Cargo LTD", "пропустить", "нетворкинг", "автоматизация", "новый", "", "", ""],
  ];
  sheet.getRange(2, 1, examples.length, 10).setValues(examples);

  // Ширина колонок
  var widths = [160, 130, 180, 130, 160, 140, 150, 200, 170, 250];
  widths.forEach(function(w, idx) { sheet.setColumnWidth(idx + 1, w); });

  // Валидация статуса (колонка D)
  var statusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["отправить", "отправлено ✅", "дожим", "ответил", "пропустить", "ошибка ❌"])
    .setAllowInvalid(false).build();
  sheet.getRange(2, COL.STATUS, 500).setDataValidation(statusRule);

  // Валидация pipeline (колонка G)
  var pipelineRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["новый", "отправлено", "ответил", "КП отправлено", "сделка", "отказ"])
    .setAllowInvalid(false).build();
  sheet.getRange(2, COL.PIPELINE, 500).setDataValidation(pipelineRule);

  // Валидация сегмента (колонка F)
  var segmentRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["рассылки", "ии-бот", "автоматизация", "всё"])
    .setAllowInvalid(false).build();
  sheet.getRange(2, COL.SEGMENT, 500).setDataValidation(segmentRule);

  Logger.log("✅ CRM-шаблон создан!");
}


// ==========================================
// ТЕСТ
// ==========================================
function testOne() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var phone = normalizePhone(String(sheet.getRange(2, COL.PHONE).getValue()));
  if (!phone) { Logger.log("Неверный номер в A2"); return; }

  var resp = sendText(phone, "Тест рассылки v3 ✅");
  Logger.log("Результат: " + resp);
}


// ==========================================
// УТИЛИТЫ
// ==========================================
function normalizePhone(raw) {
  var digits = String(raw).replace(/\D/g, '');
  if (digits.length === 11 && digits.charAt(0) === '8') digits = '7' + digits.substring(1);
  if (digits.length < 10 || digits.length > 15) return null;
  return digits;
}

function sendText(phone, text) {
  var url = SERVER_URL + "/message/sendText/" + encodeURIComponent(INSTANCE);
  var options = {
    "method": "POST",
    "headers": { "Content-Type": "application/json", "apikey": API_KEY },
    "payload": JSON.stringify({ "number": phone, "text": text }),
    "muteHttpExceptions": true
  };
  try {
    var resp = UrlFetchApp.fetch(url, options);
    var code = resp.getResponseCode();
    return (code === 200 || code === 201);
  } catch(e) {
    Logger.log("Ошибка отправки: " + e.message);
    return false;
  }
}

function sendMedia(phone, caption, mediaUrl) {
  var url = SERVER_URL + "/message/sendMedia/" + encodeURIComponent(INSTANCE);
  var mediatype = "image"; 
  var mimetype = "image/jpeg";
  
  if (mediaUrl.indexOf(".png") > -1) mimetype = "image/png";
  if (mediaUrl.indexOf(".pdf") > -1) { mediatype = "document"; mimetype = "application/pdf"; }
  if (mediaUrl.indexOf(".mp4") > -1) { mediatype = "video"; mimetype = "video/mp4"; }

  var options = {
    "method": "POST",
    "headers": { "Content-Type": "application/json", "apikey": API_KEY },
    "payload": JSON.stringify({ 
      "number": phone, 
      "mediatype": mediatype,
      "mimetype": mimetype,
      "caption": caption,
      "media": mediaUrl
    }),
    "muteHttpExceptions": true
  };
  try {
    var resp = UrlFetchApp.fetch(url, options);
    var code = resp.getResponseCode();
    return (code === 200 || code === 201);
  } catch(e) {
    Logger.log("Ошибка отправки медиа: " + e.message);
    return false;
  }
}


// ==========================================
// МЕНЮ
// ==========================================
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🚀 Рассылка')
    .addItem('▶️ Рассылка (все «отправить»)', 'sendWhatsAppMessages')
    .addItem('🔄 Дожим (follow-up молчунам)', 'sendFollowUp')
    .addItem('🏷 Рассылка по тегу', 'sendByTag')
    .addSeparator()
    .addItem('🧪 Тест 1 номера', 'testOne')
    .addItem('📋 Создать CRM-шаблон', 'createCRMTemplate')
    .addToUi();
}
