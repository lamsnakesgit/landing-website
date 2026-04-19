/**
 * WhatsApp Рассыльщик v4 — FINAL VERSION (FIXED COLS)
 * Настроено под твою таблицу (Телефон в C, Статус в D)
 */

var SERVER_URL = "https://evolutionapi.aiconicvibe.store";
var API_KEY = "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f";
var INSTANCE = "8326 301 n8n wa 1";

// НАСТРОЙКА КОЛОНОК (по твоему скриншоту)
var COL = { 
  ROW_NUM: 1,    // A (Номер строки)
  NAME: 2,       // B (ФИО)
  PHONE: 3,      // C (Номер телефона)
  STATUS: 4,     // D (Статус)
  COMPANY: 5,    // E (Название компании)
  PIPELINE: 7,   // G (Pipeline)
  LAST_SENT: 9,  // I (Чистый номер / Дата)
  MEDIA: 10      // J (Ссылка на медиа)
};

function spintax(text) {
  if (!text || typeof text !== 'string') return "";
  return text.replace(/\{([^}]+)\}/g, function(match, group) {
    var options = group.split('|');
    return options[Math.floor(Math.random() * options.length)];
  });
}

var MESSAGE_FIRST = "{Привет|Здравствуйте}, {name}! Видел вашу компанию {company}. Тестовое сообщение.";

function sendWhatsAppMessages() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0, skipped = 0, errors = 0;

  Logger.log("🚀 СТАРТ РАССЫЛКИ...");

  for (var i = 2; i <= lastRow; i++) {
    var rawPhone = String(sheet.getRange(i, COL.PHONE).getValue()).trim();
    var name = String(sheet.getRange(i, COL.NAME).getValue()).trim();
    var company = String(sheet.getRange(i, COL.COMPANY).getValue()).trim();
    var status = String(sheet.getRange(i, COL.STATUS).getValue()).trim().toLowerCase();

    if (status !== "отправить") { skipped++; continue; }
    
    var phone = normalizePhone(rawPhone);
    if (!phone) {
      Logger.log("⚠️ Строка " + i + ": нет номера");
      sheet.getRange(i, COL.STATUS).setValue("ошибка ❌");
      continue;
    }

    var message = spintax(MESSAGE_FIRST)
                    .replace(/\{name\}/g, name || "")
                    .replace(/\{company\}/g, company || "");
                    
    if (sendText(phone, message)) {
      sheet.getRange(i, COL.STATUS).setValue("отправлено ✅");
      sent++;
      Logger.log("✅ OK: " + phone);
    } else {
      errors++;
      sheet.getRange(i, COL.STATUS).setValue("ошибка ❌");
    }
    Utilities.sleep(3000);
  }
  Logger.log("🏁 ИТОГ: Отправлено " + sent);
}

function normalizePhone(raw) {
  var digits = String(raw).replace(/\D/g, '');
  return (digits.length >= 10) ? digits : null;
}

function sendText(phone, text) {
  var options = { "method":"POST", "headers":{ "Content-Type":"application/json", "apikey":API_KEY }, "payload":JSON.stringify({ "number":phone, "text":text }), "muteHttpExceptions":true };
  try { return UrlFetchApp.fetch(SERVER_URL + "/message/sendText/" + encodeURIComponent(INSTANCE), options).getResponseCode() < 300; } catch(e) { return false; }
}

function onOpen() {
  SpreadsheetApp.getUi().createMenu('🚀 Рассылка')
    .addItem('▶️ Начать рассылку', 'sendWhatsAppMessages')
    .addToUi();
}
