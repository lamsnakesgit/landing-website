document.getElementById('start').addEventListener('click', async () => {
    const numbersText = document.getElementById('numbers').value;
    const msg = document.getElementById('msg').value;
    const statusDiv = document.getElementById('status');

    const numbers = numbersText
        .split('\\n')
        .map(n => n.replace(/\\D/g, ''))
        .filter(n => n.length > 5);

    if (numbers.length === 0 || !msg) {
        statusDiv.style.color = 'red';
        statusDiv.innerText = 'Введите номера и текст сообщения!';
        return;
    }

    // Получаем текущую активную вкладку
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab.url.includes('web.whatsapp.com')) {
        statusDiv.style.color = 'red';
        statusDiv.innerText = 'Сначала откройте вкладку WhatsApp Web!';
        return;
    }

    statusDiv.style.color = '#075e54';
    statusDiv.innerText = 'Рассылка запущена! Не закрывайте эту вкладку Chrome!';

    // Запускаем скрипт внутри страницы WhatsApp Web
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: runSenderOnPage,
        args: [numbers, msg]
    });
});

// Этот скрипт выполняется внутри самой вкладки WhatsApp Web
async function runSenderOnPage(numbers, message) {
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

    for (let i = 0; i < numbers.length; i++) {
        const num = numbers[i];
        console.log(`[WA Sender] Подготовка к отправке на: ${num}`);

        // Открываем окно отправки сообщения конкретному номеру
        const link = `https://web.whatsapp.com/send?phone=${num}&text=${encodeURIComponent(message)}`;
        window.location.href = link;

        // Ждем, пока загрузится интерфейс и появится кнопка отправки
        let sendButton = null;
        let attempts = 0;
        while (!sendButton && attempts < 20) { // ждем до 20 секунд
            await sleep(1000);
            // Кнопка отправки в WhatsApp обычно имеет data-icon="send"
            sendButton = document.querySelector('button[aria-label="Send"], span[data-icon="send"]');

            // Проверяем, не вылезло ли окно "Номер не зарегистрирован"
            const invalidNumberPopup = document.querySelector('div[data-animate-modal-popup="true"]');
            if (invalidNumberPopup && invalidNumberPopup.innerText.includes('телефон')) {
                console.log(`[WA Sender] Номер ${num} не зарегистрирован в WA.`);
                const okButton = invalidNumberPopup.querySelector('button');
                if (okButton) okButton.click();
                break; // Пропускаем этот номер
            }
            attempts++;
        }

        if (sendButton) {
            // Кликаем по кнопке (часто нужно кликнуть по ее родителю)
            const clickableElement = sendButton.closest('button') || sendButton;
            clickableElement.click();
            console.log(`[WA Sender] Сообщение отправлено на: ${num}`);
            // Ждем пару секунд после отправки перед следующим
            await sleep(Math.random() * 2000 + 3000);
        } else {
            console.log(`[WA Sender] Кнопка отправки не найдена для: ${num}`);
        }
    }

    alert('Рассылка завершена!');
}
