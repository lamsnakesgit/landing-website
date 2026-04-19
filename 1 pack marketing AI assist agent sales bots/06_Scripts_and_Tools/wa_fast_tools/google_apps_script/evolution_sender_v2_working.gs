/**
 * WhatsApp Рассыльщик v2 — Google Apps Script + Evolution API
 * Рабочая версия с валидацией статусов
 * Колонки: B=имя, C=телефон, D=статус
 * Статусы: "отправить" | "отправлено ✅" | "пропустить" | "ошибка ❌"
 */

function sendWhatsAppMessages() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  var sent = 0, errors = 0;

  var SERVER_URL = "https://evolutionapi.aiconicvibe.store";
  var API_KEY = "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f";
  var INSTANCE = "8326 301 n8n wa 1";

  for (var i = 2; i <= lastRow; i++) {
    var rawPhone = String(sheet.getRange(i, 3).getValue()).trim();
    var name = String(sheet.getRange(i, 2).getValue()).trim();
    var status = String(sheet.getRange(i, 4).getValue()).trim();

    if (status === "отправлено ✅" || status === "пропустить") continue;
    if (status !== "отправить") continue;
    if (!rawPhone || rawPhone.length < 5) continue;

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
        sheet.getRange(i, 4).setValue("отправлено ✅");
        sent++;
      } else {
        sheet.getRange(i, 4).setValue("ошибка ❌");
        errors++;
      }
    } catch(e) {
      sheet.getRange(i, 4).setValue("ошибка ❌");
      errors++;
    }

    Utilities.sleep(10000);
  }

  Logger.log("Готово! Отправлено: " + sent + " | Ошибок: " + errors);
}

function testOne() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var phone = String(sheet.getRange(2, 3).getValue()).replace(/\D/g, '');
  if (phone.length === 11 && phone.charAt(0) === '8') phone = '7' + phone.substring(1);

  var url = "https://evolutionapi.aiconicvibe.store/message/sendText/" + encodeURIComponent("8326 301 n8n wa 1");
  var options = {
    "method": "POST",
    "headers": { "Content-Type": "application/json", "apikey": "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f" },
    "payload": JSON.stringify({ "number": phone, "text": "Тест рассылки ✅" }),
    "muteHttpExceptions": true
  };

  var resp = UrlFetchApp.fetch(url, options);
  Logger.log("Код: " + resp.getResponseCode() + "\n" + resp.getContentText());
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🚀 Рассылка')
    .addItem('▶️ Запустить', 'sendWhatsAppMessages')
    .addItem('🧪 Тест 1 номера', 'testOne')
    .addToUi();
}
