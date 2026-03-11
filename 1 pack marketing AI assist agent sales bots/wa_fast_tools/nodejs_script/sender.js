const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// --- НАСТРОЙКИ ---
// node sender.js [Имя_Профиля] [Файл_с_номерами]
const profileName = process.argv[2] || 'default_profile';
const file = process.argv[3] || 'numbers.txt';

/**
 * ЦЕПОЧКА СООБЩЕНИЙ (MESSAGE CHAIN)
 * Здесь ты можешь настроить любую последовательность.
 * Типы: 'text', 'image', 'video', 'audio', 'file'
 */
const messageChain = [
  { type: 'text', content: "Здравствуйте! Это первое сообщение цепочки." },
  { type: 'wait', ms: 3000 }, // Пауза 3 сек между сообщениями
  { type: 'text', content: "А вот и наше предложение в картинке! 👇" },
  // { type: 'image', path: path.join(__dirname, 'assets', 'promo.jpg'), caption: 'Наш крутой оффер!' },
];

async function run() {
  console.log(`🚀 Запуск WA Fast Sender (ULTRA Edition - Chains & Media)`);
  console.log(`👤 Профиль: ${profileName}`);

  if (!fs.existsSync(file)) {
    console.log(`❌ ОШИБКА: Файл ${file} не найден.`);
    process.exit(1);
  }
  const numbers = fs.readFileSync(file, 'utf8')
    .split('\n')
    .map(n => n.replace(/\D/g, ''))
    .filter(n => n.length > 5);

  console.log(`📋 Загружено номеров: ${numbers.length}`);

  const userDataDir = path.join(__dirname, 'profiles', profileName);

  console.log(`\n⏳ Запускаем браузер...`);
  const browser = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    channel: 'chrome',
    viewport: { width: 1000, height: 800 }
  });

  const page = await browser.newPage();
  await page.goto('https://web.whatsapp.com');

  console.log('📱 Ожидание загрузки WhatsApp Web...');
  await page.waitForSelector('#pane-side', { timeout: 0 });
  console.log('✅ Авторизация успешна!\n');

  for (let i = 0; i < numbers.length; i++) {
    const num = numbers[i];
    console.log(`[${i + 1}/${numbers.length}] Работаем с номером: ${num}`);

    try {
      // 1. Открываем чат
      await page.goto(`https://web.whatsapp.com/send?phone=${num}`);
      
      const sendButtonSelector = 'button[aria-label="Send"], span[data-icon="send"]';
      const invalidPopupSelector = 'div[data-animate-modal-popup="true"]';

      // Ждем загрузки чата
      await Promise.race([
        page.waitForSelector('div[contenteditable="true"]', { state: 'visible', timeout: 30000 }),
        page.waitForSelector(invalidPopupSelector, { state: 'visible', timeout: 30000 })
      ]);

      const isInvalid = await page.$(invalidPopupSelector);
      if (isInvalid) {
        console.log(`❌ Номер ${num} не в WhatsApp. Пропуск.`);
        await page.click(`${invalidPopupSelector} button`);
        continue;
      }

      // 2. Проходим по цепочке сообщений
      for (const step of messageChain) {
        if (step.type === 'text') {
          console.log(`  ✉️ Отправка текста: ${step.content.substring(0, 20)}...`);
          const input = await page.waitForSelector('div[contenteditable="true"]');
          await input.fill(step.content);
          await page.keyboard.press('Enter');
        } else if (step.type === 'wait') {
          console.log(`  ⏳ Пауза ${step.ms}мс...`);
          await page.waitForTimeout(step.ms);
        } else if (['image', 'video', 'audio', 'file'].includes(step.type)) {
          console.log(`  📎 Отправка медиа (${step.type}): ${path.basename(step.path)}`);
          if (!fs.existsSync(step.path)) {
            console.log(`  ⚠️ Файл не найден: ${step.path}`);
            continue;
          }
          // Нажимаем "Плюс" или "Скрепку"
          await page.click('div[aria-label="Attach"], span[data-icon="plus"]');
          const fileInput = await page.waitForSelector('input[type="file"]');
          await fileInput.setInputFiles(step.path);
          
          // Ждем кнопку отправки в превью медиа
          const mediaSendBtn = await page.waitForSelector('span[data-icon="send"]', { timeout: 10000 });
          
          // Если есть подпись (caption)
          if (step.caption) {
            const captionInput = await page.locator('div[contenteditable="true"]').nth(1);
            await captionInput.fill(step.caption);
          }
          
          await mediaSendBtn.click();
        }
        await page.waitForTimeout(1000); // Мини-пауза между шагами цепочки
      }

      console.log(`✅ Цепочка для ${num} завершена.`);
      
      // Глобальная пауза между контактами (рандом)
      await page.waitForTimeout(Math.floor(Math.random() * 5000 + 5000));

    } catch (e) {
      console.log(`⚠️ Сбой на номере ${num}: ${e.message}`);
    }
  }

  console.log(`\n🎉 ВСЁ ГОТОВО! Бот закончил работу.`);
}

run();
