const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// --- НАСТРОЙКИ ---
// Берем параметры из командной строки: 
// node sender.js [Имя_Профиля] [Файл_с_номерами]
const profileName = process.argv[2] || 'default_profile';
const file = process.argv[3] || 'numbers.txt';

// Сообщение по умолчанию
const defaultMessage = "Здравствуйте! Это тестовое сообщение.";

async function run() {
    console.log(`🚀 Запуск WA Fast Sender (Node.js Edition)`);
    console.log(`👤 Профиль: ${profileName}`);

    // Чтение номеров из файла (очистка от нецифр)
    if (!fs.existsSync(file)) {
        console.log(`❌ ОШИБКА: Файл ${file} не найден. Создайте его и добавьте номера.`);
        process.exit(1);
    }
    const numbers = fs.readFileSync(file, 'utf8')
        .split('\\n')
        .map(n => n.replace(/\\D/g, ''))
        .filter(n => n.length > 5);

    console.log(`📋 Загружено номеров: ${numbers.length}`);

    // Папка для хранения сессии (чтобы не сканировать QR каждый раз)
    const userDataDir = path.join(__dirname, 'profiles', profileName);

    console.log(`\n⏳ Запускаем браузер...`);
    // Запускаем Chromium с постоянным профилем (Persistent Context)
    const browser = await chromium.launchPersistentContext(userDataDir, {
        headless: false, // ВИДИМЫЙ РЕЖИМ для демонстрации
        channel: 'chrome', // Использовать обычный Chrome (если установлен)
        viewport: { width: 1000, height: 800 }
    });

    const page = await browser.newPage();
    await page.goto('https://web.whatsapp.com');

    console.log('📱 Ожидание загрузки WhatsApp Web...');
    console.log('⚠️ Если вы используете этот профиль впервые, ОТСКАНИРУЙТЕ QR-КОД.');

    // Ждем появления панели чатов (признак успешного входа)
    await page.waitForSelector('#pane-side', { timeout: 0 }); // timeout 0 = ждем бесконечно
    console.log('✅ Авторизация успешна! Начинаем рассылку через 3 секунды...\n');
    await page.waitForTimeout(3000);

    let successCount = 0;

    for (let i = 0; i < numbers.length; i++) {
        const num = numbers[i];
        console.log(`[${i + 1}/${numbers.length}] Подготовка отправки на номер: ${num}`);

        try {
            // Переходим по прямой ссылке для отправки
            const url = `https://web.whatsapp.com/send?phone=${num}&text=${encodeURIComponent(defaultMessage)}`;
            await page.goto(url);

            // Ждем либо кнопку отправки, либо всплывающего окна "номер не зарегистрирован"
            const sendButtonSelector = 'button[aria-label="Send"], span[data-icon="send"]';
            const invalidPopupSelector = 'div[data-animate-modal-popup="true"]';

            // Ждем появления одного из двух элементов (таймаут 20 секунд)
            await Promise.race([
                page.waitForSelector(sendButtonSelector, { state: 'visible', timeout: 20000 }),
                page.waitForSelector(invalidPopupSelector, { state: 'visible', timeout: 20000 })
            ]);

            // Проверяем, не ошибка ли это
            const isInvalid = await page.$(invalidPopupSelector);
            if (isInvalid) {
                const text = await page.innerText(invalidPopupSelector);
                if (text.includes('зарегистрирован') || text.includes('not on WhatsApp')) {
                    console.log(`❌ ОШИБКА: Номер ${num} не существует в WhatsApp. Пропуск.`);
                    // Нажимаем Ок чтобы закрыть модалку
                    await page.click(`${invalidPopupSelector} button`);
                    continue;
                }
            }

            // Если ошибки нет, жмем кнопку отправки
            await page.click(sendButtonSelector);
            console.log(`✅ УСПЕШНО: Сообщение отправлено на ${num}`);
            successCount++;

            // Защитная пауза (имитация человека: 2.5 - 5 секунд)
            const pauseStr = Math.floor(Math.random() * 2500 + 2500);
            await page.waitForTimeout(pauseStr);

        } catch (e) {
            console.log(`⚠️ ПРЕДУПРЕЖДЕНИЕ: Не удалось отправить на ${num}. Возможно долгая загрузка или сбой селекторов.`);
        }
    }

    console.log(`\n🎉 ГОТОВО! Успешно отправлено: ${successCount} из ${numbers.length}`);
    console.log('Браузер останется открытым. Закройте его вручную, когда завершите.');
}

run();
