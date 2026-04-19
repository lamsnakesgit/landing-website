/**
 * WhatsApp Рассыльщик v4 — CRM + Spintax + Follow-up + Отчёты + Таймер + Ответы
 * 
 * ЛИСТЫ:
 *   "CRM"     — основная база контактов
 *   "Отчёты"  — лог всех рассылок (дата, кол-во, статус)
 *   "Ответы"  — кто ответил (автоопределение)
 * 
 * CRM-КОЛОНКИ (A-J):
 *   A=phone | B=name | C=company | D=status | E=tag | F=segment | G=pipeline | H=notes | I=last_sent | J=прочитано
 * 
 * СТАТУСЫ: отправить | отправлено ✅ | дожим | ответил | пропустить | ошибка ❌
 * PIPELINE: новый → отправлено → ответил → КП отправлено → сделка → отказ
 */

// === НАСТРОЙКИ ===
var SERVER_URL = "https://evolutionapi.aiconicvibe.store";
var API_KEY = "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f";
var INSTANCE = "8326 301 n8n wa 1";

// Сколько сообщений за один запуск таймера (батч)
var BATCH_SIZE = 10;

// === КОЛОНКИ CRM ===
var COL = { PHONE: 1, NAME: 2, COMPANY: 3, STATUS: 4, TAG: 5, SEGMENT: 6, PIPELINE: 7, NOTES: 8, LAST_SENT: 9, READ: 10 };

// === ИМЕНА ЛИСТОВ ===
var SHEET_CRM = "CRM";
var SHEET_REPORTS = "Отчёты";
var SHEET_REPLIES = "Ответы";


// ==========================================
// SPINTAX
// ==========================================
function spintax(text) {
  return text.replace(/\{([^}]+)\}/g, function(match, group) {
    var options = group.split('|');
    return options[Math.floor(Math.random() * options.length)];
  });
}

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
  var sheet = getCRMSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0, errors = 0;
  var startTime = new Date();

  for (var i = 2; i <= lastRow; i++) {
    var rawPhone = String(sheet.getRange(i, COL.PHONE).getValue()).trim();
    var name = String(sheet.getRange(i, COL.NAME).getValue()).trim();
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim();

    if (status !== "отправить") continue;
    if (!rawPhone || rawPhone.length < 5) continue;

    var phone = normalizePhone(rawPhone);
    if (!phone) { sheet.getRange(i, COL.STATUS).setValue("ошибка ❌"); errors++; continue; }

    var message = spintax(MESSAGE_FIRST).replace(/\{name\}/g, name || "");

    if (sendText(phone, message)) {
      sheet.getRange(i, COL.STATUS).setValue("отправлено ✅");
      sheet.getRange(i, COL.PIPELINE).setValue("отправлено");
      sheet.getRange(i, COL.LAST_SENT).setValue(new Date().toLocaleString());
      sent++;
    } else {
      sheet.getRange(i, COL.STATUS).setValue("ошибка ❌");
      errors++;
    }

    Utilities.sleep(8000 + Math.floor(Math.random() * 7000));
  }

  logReport("Рассылка", startTime, sent, errors);
  Logger.log("РАССЫЛКА: ✅ " + sent + " | ❌ " + errors);
}


// ==========================================
// ДОЖИМ (Follow-up)
// ==========================================
function sendFollowUp() {
  var sheet = getCRMSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0;
  var startTime = new Date();

  for (var i = 2; i <= lastRow; i++) {
    var rawPhone = String(sheet.getRange(i, COL.PHONE).getValue()).trim();
    var name = String(sheet.getRange(i, COL.NAME).getValue()).trim();
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim();

    if (status !== "отправлено ✅") continue;

    var phone = normalizePhone(rawPhone);
    if (!phone) continue;

    var message = spintax(MESSAGE_FOLLOWUP).replace(/\{name\}/g, name || "");

    if (sendText(phone, message)) {
      sheet.getRange(i, COL.STATUS).setValue("дожим");
      sheet.getRange(i, COL.LAST_SENT).setValue(new Date().toLocaleString());
      sent++;
    }

    Utilities.sleep(10000 + Math.floor(Math.random() * 10000));
  }

  logReport("Дожим", startTime, sent, 0);
  Logger.log("ДОЖИМ: ✅ " + sent);
}


// ==========================================
// РАССЫЛКА ПО ТЕГУ
// ==========================================
function sendByTag() {
  var ui = SpreadsheetApp.getUi();
  var result = ui.prompt('Введите тег', 'Например: клиент', ui.ButtonSet.OK_CANCEL);
  if (result.getSelectedButton() !== ui.Button.OK) return;
  
  var targetTag = result.getResponseText().trim().toLowerCase();
  var sheet = getCRMSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0;
  var startTime = new Date();

  for (var i = 2; i <= lastRow; i++) {
    var tags = String(sheet.getRange(i, COL.TAG).getValue()).toLowerCase();
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim();
    if (tags.indexOf(targetTag) === -1 || status !== "отправить") continue;

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

  logReport("По тегу: " + targetTag, startTime, sent, 0);
}


// ==========================================
// ТАЙМЕР — АВТООТПРАВКА БАТЧАМИ
// ==========================================
function timerSendBatch() {
  var sheet = getCRMSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0;
  var startTime = new Date();

  for (var i = 2; i <= lastRow && sent < BATCH_SIZE; i++) {
    var rawPhone = String(sheet.getRange(i, COL.PHONE).getValue()).trim();
    var name = String(sheet.getRange(i, COL.NAME).getValue()).trim();
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim();

    if (status !== "отправить") continue;
    if (!rawPhone || rawPhone.length < 5) continue;

    var phone = normalizePhone(rawPhone);
    if (!phone) { sheet.getRange(i, COL.STATUS).setValue("ошибка ❌"); continue; }

    var message = spintax(MESSAGE_FIRST).replace(/\{name\}/g, name || "");

    if (sendText(phone, message)) {
      sheet.getRange(i, COL.STATUS).setValue("отправлено ✅");
      sheet.getRange(i, COL.PIPELINE).setValue("отправлено");
      sheet.getRange(i, COL.LAST_SENT).setValue(new Date().toLocaleString());
      sent++;
    }

    Utilities.sleep(8000 + Math.floor(Math.random() * 7000));
  }

  if (sent > 0) logReport("Таймер (батч " + BATCH_SIZE + ")", startTime, sent, 0);
  Logger.log("ТАЙМЕР: отправлено " + sent + " из батча " + BATCH_SIZE);
}

// Включить автоотправку каждый час
function enableTimer() {
  ScriptApp.newTrigger('timerSendBatch')
    .timeBased()
    .everyHours(1)
    .create();
  Logger.log("✅ Таймер включён! Каждый час будет отправлять по " + BATCH_SIZE + " сообщений");
}

// Выключить таймер
function disableTimer() {
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(t) {
    if (t.getHandlerFunction() === 'timerSendBatch') {
      ScriptApp.deleteTrigger(t);
    }
  });
  Logger.log("⏹ Таймер выключен");
}


// ==========================================
// ПРОВЕРКА ОТВЕТОВ (через Evolution API)
// ==========================================
function checkReplies() {
  var sheet = getCRMSheet();
  var repliesSheet = getRepliesSheet();
  var lastRow = sheet.getLastRow();
  var found = 0;

  for (var i = 2; i <= lastRow; i++) {
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim();
    // Проверяем только тех, кому отправляли
    if (status !== "отправлено ✅" && status !== "дожим") continue;

    var rawPhone = String(sheet.getRange(i, COL.PHONE).getValue()).trim();
    var phone = normalizePhone(rawPhone);
    if (!phone) continue;

    // Запрос к Evolution API — последние сообщения для этого чата
    var chatMessages = fetchMessagesFromChat(phone);
    if (!chatMessages || chatMessages.length === 0) continue;

    // Ищем входящие (fromMe: false)
    var hasReply = false;
    var lastReplyText = "";
    for (var m = 0; m < chatMessages.length; m++) {
      if (chatMessages[m].key && chatMessages[m].key.fromMe === false) {
        hasReply = true;
        lastReplyText = chatMessages[m].message && chatMessages[m].message.conversation 
          ? chatMessages[m].message.conversation 
          : "(медиа/стикер)";
        break;
      }
    }

    if (hasReply) {
      // Обновляем CRM
      sheet.getRange(i, COL.STATUS).setValue("ответил");
      sheet.getRange(i, COL.PIPELINE).setValue("ответил");
      
      // Записываем в лист Ответы
      var name = String(sheet.getRange(i, COL.NAME).getValue()).trim();
      var nextRow = repliesSheet.getLastRow() + 1;
      repliesSheet.getRange(nextRow, 1, 1, 4).setValues([
        [new Date().toLocaleString(), phone, name, lastReplyText.substring(0, 200)]
      ]);
      found++;
    }
  }

  if (found > 0) logReport("Проверка ответов", new Date(), found, 0);
  Logger.log("ОТВЕТЫ: найдено " + found + " новых ответов");
}

function fetchMessagesFromChat(phone) {
  var jid = phone + "@s.whatsapp.net";
  var url = SERVER_URL + "/chat/findMessages/" + encodeURIComponent(INSTANCE);
  
  var options = {
    "method": "POST",
    "headers": { "Content-Type": "application/json", "apikey": API_KEY },
    "payload": JSON.stringify({ "where": { "key": { "remoteJid": jid } }, "limit": 5 }),
    "muteHttpExceptions": true
  };

  try {
    var resp = UrlFetchApp.fetch(url, options);
    if (resp.getResponseCode() === 200) {
      return JSON.parse(resp.getContentText());
    }
  } catch(e) {
    Logger.log("Ошибка получения сообщений для " + phone + ": " + e.message);
  }
  return [];
}

// Включить автопроверку ответов каждые 30 мин
function enableReplyChecker() {
  ScriptApp.newTrigger('checkReplies')
    .timeBased()
    .everyMinutes(30)
    .create();
  Logger.log("✅ Проверка ответов включена (каждые 30 мин)");
}

function disableReplyChecker() {
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(t) {
    if (t.getHandlerFunction() === 'checkReplies') {
      ScriptApp.deleteTrigger(t);
    }
  });
  Logger.log("⏹ Проверка ответов выключена");
}


// ==========================================
// ЛИСТ ОТЧЁТОВ
// ==========================================
function logReport(type, startTime, sent, errors) {
  var reportSheet = getReportSheet();
  var endTime = new Date();
  var duration = Math.round((endTime - startTime) / 1000);
  
  var nextRow = reportSheet.getLastRow() + 1;
  reportSheet.getRange(nextRow, 1, 1, 6).setValues([[
    endTime.toLocaleString(),
    type,
    startTime.toLocaleTimeString(),
    endTime.toLocaleTimeString(),
    sent,
    errors
  ]]);
}


// ==========================================
// СОЗДАТЬ CRM + ОТЧЁТЫ + ОТВЕТЫ
// ==========================================
function createCRMTemplate() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // --- Лист CRM ---
  var crm = ss.getSheetByName(SHEET_CRM) || ss.insertSheet(SHEET_CRM);
  var crmHeaders = [["📱 Телефон", "👤 Имя", "🏢 Компания", "📊 Статус", "🏷 Теги", "🎯 Сегмент", "📈 Воронка", "📝 Заметки", "🕐 Посл. касание", "👁 Прочитано"]];
  crm.getRange(1, 1, 1, 10).setValues(crmHeaders).setFontWeight("bold").setBackground("#1a73e8").setFontColor("white");
  
  var examples = [
    ["+7 999 123 4567", "Анна", "ООО Логистик", "отправить", "клиент", "рассылки", "новый", "", "", ""],
    ["89991234567", "Иван", "ИП Петров", "отправить", "клиент, партнёр", "ии-бот", "новый", "С конференции", "", ""],
  ];
  crm.getRange(2, 1, examples.length, 10).setValues(examples);

  var widths = [160, 130, 180, 130, 160, 140, 150, 200, 150, 100];
  widths.forEach(function(w, idx) { crm.setColumnWidth(idx + 1, w); });

  // Валидации
  var statusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["отправить", "отправлено ✅", "дожим", "ответил", "пропустить", "ошибка ❌"])
    .setAllowInvalid(false).build();
  crm.getRange(2, COL.STATUS, 1000).setDataValidation(statusRule);

  var pipelineRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["новый", "отправлено", "ответил", "КП отправлено", "сделка", "отказ"])
    .setAllowInvalid(false).build();
  crm.getRange(2, COL.PIPELINE, 1000).setDataValidation(pipelineRule);

  var segmentRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["рассылки", "ии-бот", "автоматизация", "всё"])
    .setAllowInvalid(false).build();
  crm.getRange(2, COL.SEGMENT, 1000).setDataValidation(segmentRule);

  // --- Лист Отчёты ---
  var reports = ss.getSheetByName(SHEET_REPORTS) || ss.insertSheet(SHEET_REPORTS);
  reports.getRange(1, 1, 1, 6).setValues([["📅 Дата", "📋 Тип", "⏰ Старт", "⏰ Конец", "✅ Отправлено", "❌ Ошибок"]])
    .setFontWeight("bold").setBackground("#34a853").setFontColor("white");
  [180, 180, 120, 120, 130, 130].forEach(function(w, idx) { reports.setColumnWidth(idx + 1, w); });

  // --- Лист Ответы ---
  var replies = ss.getSheetByName(SHEET_REPLIES) || ss.insertSheet(SHEET_REPLIES);
  replies.getRange(1, 1, 1, 4).setValues([["📅 Дата", "📱 Телефон", "👤 Имя", "💬 Ответ"]])
    .setFontWeight("bold").setBackground("#ea4335").setFontColor("white");
  [180, 160, 150, 400].forEach(function(w, idx) { replies.setColumnWidth(idx + 1, w); });

  Logger.log("✅ CRM + Отчёты + Ответы — всё создано!");
}


// ==========================================
// ТЕСТ
// ==========================================
function testOne() {
  var sheet = getCRMSheet();
  var phone = normalizePhone(String(sheet.getRange(2, COL.PHONE).getValue()));
  if (!phone) { Logger.log("Неверный номер"); return; }
  var ok = sendText(phone, "Тест v4 ✅");
  Logger.log("Результат: " + (ok ? "✅ отправлено" : "❌ ошибка"));
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
    return (resp.getResponseCode() === 200 || resp.getResponseCode() === 201);
  } catch(e) {
    Logger.log("Ошибка: " + e.message);
    return false;
  }
}

function getCRMSheet() {
  return SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_CRM) 
    || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
}

function getReportSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(SHEET_REPORTS) || ss.insertSheet(SHEET_REPORTS);
}

function getRepliesSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(SHEET_REPLIES) || ss.insertSheet(SHEET_REPLIES);
}


// ==========================================
// МЕНЮ
// ==========================================
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🚀 Рассылка')
    .addItem('▶️ Рассылка (все «отправить»)', 'sendWhatsAppMessages')
    .addItem('🔄 Дожим (follow-up)', 'sendFollowUp')
    .addItem('🏷 Рассылка по тегу', 'sendByTag')
    .addSeparator()
    .addItem('🔍 Проверить ответы', 'checkReplies')
    .addSeparator()
    .addSubMenu(ui.createMenu('⏰ Таймер')
      .addItem('▶ Включить (каждый час)', 'enableTimer')
      .addItem('⏹ Выключить', 'disableTimer'))
    .addSubMenu(ui.createMenu('👁 Авто-проверка ответов')
      .addItem('▶ Включить (каждые 30 мин)', 'enableReplyChecker')
      .addItem('⏹ Выключить', 'disableReplyChecker'))
    .addSeparator()
    .addItem('🧪 Тест 1 номера', 'testOne')
    .addItem('📋 Создать CRM (3 листа)', 'createCRMTemplate')
    .addToUi();
}
