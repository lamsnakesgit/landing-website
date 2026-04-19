/**
 * WhatsApp Рассыльщик — Google Apps Script + Evolution API
 * Колонки: A=phone, B=name, C=company, D=status
 * Запуск: Меню "🚀 Рассылка" в таблице
 */

var SERVER_URL = "https://evolutionapi.aiconicvibe.store";
var API_KEY = "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f";
var INSTANCE = "8326 301 n8n wa 1";

// === КОЛОНКИ (меняй под свою таблицу) ===
var COL_PHONE = 1;   // A
var COL_NAME = 2;    // B
var COL_COMPANY = 3; // C
var COL_STATUS = 4;  // D

function sendWhatsAppMessages() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0, errors = 0;
  
  for (var i = 2; i <= lastRow; i++) {
    var rawPhone = String(sheet.getRange(i, COL_PHONE).getValue()).trim();
    var name = String(sheet.getRange(i, COL_NAME).getValue()).trim();
    var status = String(sheet.getRange(i, COL_STATUS).getValue()).trim();
    
    // Пропуск уже отправленных и пустых
    if (status.indexOf("✅") !== -1) continue;
    if (!rawPhone || rawPhone.length < 5) continue;
    
    // Нормализация: убираем всё кроме цифр, 8→7
    var phone = rawPhone.replace(/\D/g, '');
    if (phone.length === 11 && phone.charAt(0) === '8') {
      phone = '7' + phone.substring(1);
    }
    
    var message = "Привет, " + (name || "") + "! \n\n" +
              "Занимаюсь автоматизацией продаж через ИИ и WhatsApp рассылки.\n\n" +
              "Помогаю находить клиентов на автопилоте - без холодных звонков и ручных переписок.\n\n" +
              "Интересно узнать как это работает?\n\n" +
              "Ответьте на это сообщение если интересно";

    var url = SERVER_URL + "/message/sendText/" + encodeURIComponent(INSTANCE);
    
    var options = {
      "method": "POST",
      "headers": { "Content-Type": "application/json", "apikey": API_KEY },
      "payload": JSON.stringify({ "number": phone, "text": message }),
      "muteHttpExceptions": true
    };
    
    try {
      var response = UrlFetchApp.fetch(url, options);
      var code = response.getResponseCode();
      if (code === 200 || code === 201) {
        sheet.getRange(i, COL_STATUS).setValue("✅ Отправлено");
        sent++;
      } else {
        var body = response.getContentText().substring(0, 80);
        sheet.getRange(i, COL_STATUS).setValue("❌ " + code + ": " + body);
        errors++;
      }
    } catch(e) {
      sheet.getRange(i, COL_STATUS).setValue("❌ " + e.message);
      errors++;
    }
    
    Utilities.sleep(10000); // 10 сек пауза
  }
  
  Logger.log("Готово! ✅ " + sent + " отправлено, ❌ " + errors + " ошибок");
}

// === СОЗДАТЬ ШАБЛОН ТАБЛИЦЫ ===
function createTemplate() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getActiveSheet();
  
  // Заголовки
  var headers = [["📱 Телефон", "👤 Имя", "🏢 Компания", "📊 Статус"]];
  sheet.getRange(1, 1, 1, 4).setValues(headers);
  sheet.getRange(1, 1, 1, 4).setFontWeight("bold");
  sheet.getRange(1, 1, 1, 4).setBackground("#4285f4");
  sheet.getRange(1, 1, 1, 4).setFontColor("white");
  
  // Примеры
  var examples = [
    ["+7 999 123 4567", "Анна", "ООО Логистик", ""],
    ["89991234567", "Иван", "ИП Петров", ""],
    ["8 705 739 6014", "Валерий", "", ""],
  ];
  sheet.getRange(2, 1, examples.length, 4).setValues(examples);
  
  // Ширина колонок
  sheet.setColumnWidth(1, 180);
  sheet.setColumnWidth(2, 150);
  sheet.setColumnWidth(3, 200);
  sheet.setColumnWidth(4, 200);
  
  Logger.log("✅ Шаблон создан!");
}

// === ТЕСТ 1 НОМЕРА ===
function testOne() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var phone = String(sheet.getRange(2, COL_PHONE).getValue()).replace(/\D/g, '');
  if (phone.length === 11 && phone.charAt(0) === '8') phone = '7' + phone.substring(1);
  
  var url = SERVER_URL + "/message/sendText/" + encodeURIComponent(INSTANCE);
  var options = {
    "method": "POST",
    "headers": { "Content-Type": "application/json", "apikey": API_KEY },
    "payload": JSON.stringify({ "number": phone, "text": "Тест рассылки ✅" }),
    "muteHttpExceptions": true
  };
  
  var resp = UrlFetchApp.fetch(url, options);
  Logger.log("Код: " + resp.getResponseCode() + "\n" + resp.getContentText().substring(0, 300));
}

// === МЕНЮ ===
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🚀 Рассылка')
    .addItem('▶️ Запустить', 'sendWhatsAppMessages')
    .addItem('🧪 Тест 1 номера', 'testOne')
    .addItem('📋 Создать шаблон таблицы', 'createTemplate')
    .addToUi();
}
