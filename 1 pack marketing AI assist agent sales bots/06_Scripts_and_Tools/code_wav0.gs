// function myFunction() {
  
// }
function sendWhatsAppMessages() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  
  // Твои данные Evolution API
  var SERVER_URL = "https://evolutionapi.aiconicvibe.store"; //http://localhost:8081"//"http://ТВО_ВПС_IP:8080"; // твой сервер
  var API_KEY = "b5485840231d596018f5d67b50b4a05ffaaa792cec60595f"//"ТВО_API_KEY"; // твой ключ
  var INSTANCE = "8326 301 n8n wa 1"//"ИМЯ_ИНСТАНЦИИ"; // название инстанции
  
  for (var i = 2; i <= lastRow; i++) {
    var phone = sheet.getRange(i, 1).getValue(); // колонка A — номер
    var name = sheet.getRange(i, 2).getValue();  // колонка B — имя
    var status = sheet.getRange(i, 3).getValue(); // колонка C — статус
    
    // Отправляем только строки со статусом "отправить"
    if (status !== "отправить") continue;
    
    // var message = "Привет, " + name + "! 👋\n\n" +
    //               "ТУТ ТЕКСТ АСЕЛИ\n\n" +
    //               "Ответьте на это сообщение если интересно 😊";
    // var message = "Привет, " + name + "! 👋\n\n" +
    //               "Занимаюсь автоматизацией продаж для дизайнеров через ИИ и WhatsApp рассылки.

    //     Помогаю находить клиентов на автопилоте — без холодных звонков и ручных переписок.

    //   Интересно узнать как это работает? 😊\n\n" +
    //               "Ответьте на это сообщение если интересно 😊";
    var message = "Привет, " + name + "! \n\n" +
              "Занимаюсь автоматизацией продаж через ИИ и WhatsApp рассылки.\n\n" +
              "Помогаю находить клиентов на автопилоте - без холодных звонков и ручных переписок.\n\n" +
              "Интересно узнать как это работает? \n\n" +
              "Ответьте на это сообщение если интересно";

    var url = SERVER_URL + "/message/sendText/" + INSTANCE;
    
    var payload = {
      //"number": phone + "@s.whatsapp.net",
      "number": String(phone).replace(/\D/g, ''), // только цифры, без @s.whatsapp.net
      "text": message
    };
    
    var options = {
      "method": "POST",
      "headers": {
        "Content-Type": "application/json",
        "apikey": API_KEY
      },
      "payload": JSON.stringify(payload),
      "muteHttpExceptions": true
    };
    
    try {
      var response = UrlFetchApp.fetch(url, options);
      // Ставим статус "отправлено"
      sheet.getRange(i, 3).setValue("отправлено ✅");
      Utilities.sleep(30000); // пауза 30 сек между сообщениями
    } catch(e) {
      sheet.getRange(i, 3).setValue("ошибка ❌");
    }
  }

}
  function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🚀 Рассылка')
    .addItem('▶️ Запустить рассылку', 'sendWhatsAppMessages')
    .addToUi();
}
