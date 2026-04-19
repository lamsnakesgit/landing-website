// function myFunction() {
  
// }
function sendWhatsAppMessages() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();

  var SERVER_URL = "http://ТВОй_ВПС_IP:8080";
  var API_KEY = "ТВОй_API_KEY";
  var INSTANCE = "ИМЯ_ИНСТАНЦИИ";

  for (var i = 3; i <= lastRow; i++) {
    var phone = sheet.getRange(i, 11).getValue();  // колонка K — чистый номер
    var name = sheet.getRange(i, 2).getValue();    // колонка B — имя
    var status = sheet.getRange(i, 4).getValue();  // колонка D — статус

    if (status !== "отправить") continue;
    if (!phone) continue;

    var message = "Привет, " + name + "!\n\n" +
                  "Занимаюсь автоматизацией продаж через ИИ и WhatsApp рассылки.\n\n" +
                  "Помогаю находить клиентов на автопилоте - без холодных звонков.\n\n" +
                  "Интересно узнать как это работает?";

    var url = SERVER_URL + "/message/sendText/" + INSTANCE;

    var payload = {
      "number": phone + "@s.whatsapp.net",
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
      var code = response.getResponseCode();
      if (code === 200 || code === 201) {
        sheet.getRange(i, 4).setValue("отправлено ✅");
      } else {
        sheet.getRange(i, 4).setValue("ошибка " + code + " ❌");
      }
    } catch(e) {
      sheet.getRange(i, 4).setValue("ошибка ❌");
    }

    Utilities.sleep(30000); // пауза 30 сек между сообщениями — защита от бана
  }
}

