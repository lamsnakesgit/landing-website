const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Вспомогательная функция для задержки
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Пути к папкам экспорта
const EXPORT_DIR = path.join(__dirname, '../assets/exported');
const IMAGES_DIR = path.join(EXPORT_DIR, 'images');
const VIDEO_DIR = path.join(EXPORT_DIR, 'video');
const TEMP_VIDEO_DIR = path.join(VIDEO_DIR, 'temp');

// Создаем необходимые директории
if (!fs.existsSync(EXPORT_DIR)) fs.mkdirSync(EXPORT_DIR, { recursive: true });
if (!fs.existsSync(IMAGES_DIR)) fs.mkdirSync(IMAGES_DIR, { recursive: true });
if (!fs.existsSync(VIDEO_DIR)) fs.mkdirSync(VIDEO_DIR, { recursive: true });
if (!fs.existsSync(TEMP_VIDEO_DIR)) fs.mkdirSync(TEMP_VIDEO_DIR, { recursive: true });

async function run() {
    console.log('=== НАЧАЛО ЭКСПОРТА ПРЕЗЕНТАЦИИ ===');
    
    const browser = await chromium.launch({ headless: true });
    const localHtmlPath = `file://${path.resolve(__dirname, '../index.html')}`;
    
    // ==========================================
    // ЭТАП 1: ... Скриншоты слайдов (PNG 1080x1350)
    // ==========================================
    console.log('\n--- Шаг 1: Генерация статических картинок (PNG)...');
    
    // Вьюпорт 360x450 (соотношение 4:5) с масштабированием x3 дает ровно 1080x1350px
    const imgContext = await browser.newContext({
        viewport: { width: 360, height: 450 },
        deviceScaleFactor: 3
    });
    
    const imgPage = await imgContext.newPage();
    console.log(`Открываем страницу: ${localHtmlPath}`);
    await imgPage.goto(localHtmlPath);
    
    // Ждем полной загрузки и готовности шрифтов
    await imgPage.waitForLoadState('networkidle');
    await imgPage.evaluate(() => document.fonts.ready);
    
    // Включаем режим экспорта (скрывает лишние кнопки и интерфейсы)
    await imgPage.evaluate(() => document.body.classList.add('export-mode'));
    
    const totalSlides = 5;
    for (let i = 0; i < totalSlides; i++) {
        console.log(`Рендеринг слайда ${i + 1} из ${totalSlides}...`);
        
        // Ждем завершения анимаций появления контента
        await delay(2500);
        
        // Делаем скриншот слайда
        const screenshotPath = path.join(IMAGES_DIR, `slide_${i + 1}.png`);
        await imgPage.screenshot({ path: screenshotPath, type: 'png' });
        console.log(`Сохранен: assets/exported/images/slide_${i + 1}.png`);
        
        // Переходим к следующему слайду нажатием клавиши "ArrowDown"
        if (i < totalSlides - 1) {
            await imgPage.keyboard.press('ArrowDown');
        }
    }
    
    await imgContext.close();
    
    // ==========================================
    // ЭТАП 2: Запись видео (MP4 1080x1920 / 9:16)
    // ==========================================
    console.log('\n--- Шаг 2: Запись видеопрезентации (Reels/Stories 9:16)...');
    
    // Для записи видео в Playwright используем вьюпорт 360x640 (9:16) и масштаб x3
    const videoContext = await browser.newContext({
        viewport: { width: 360, height: 640 },
        deviceScaleFactor: 3,
        recordVideo: {
            dir: TEMP_VIDEO_DIR,
            size: { width: 1080, height: 1920 }
        }
    });
    
    const videoPage = await videoContext.newPage();
    await videoPage.goto(localHtmlPath);
    await videoPage.waitForLoadState('networkidle');
    await videoPage.evaluate(() => document.fonts.ready);
    await videoPage.evaluate(() => document.body.classList.add('export-mode'));
    
    // Тайминги задержек для каждого слайда в миллисекундах (чтобы пользователь успел прочитать)
    const slideTimings = [
        5000,  // Слайд 1: Титульный (5 сек)
        6000,  // Слайд 2: Шаг 1 (6 сек)
        6500,  // Слайд 3: Шаг 2 (6.5 сек)
        6000,  // Слайд 4: Шаг 3 (6 сек)
        8000   // Слайд 5: Итоги (8 сек)
    ];
    
    for (let i = 0; i < totalSlides; i++) {
        console.log(`Запись слайда ${i + 1} (${slideTimings[i] / 1000} сек)...`);
        
        // Ждем указанное время на слайде
        await delay(slideTimings[i]);
        
        // Переходим к следующему слайду нажатием клавиши "ArrowDown"
        if (i < totalSlides - 1) {
            await videoPage.keyboard.press('ArrowDown');
        }
    }
    
    // Получаем путь к записанному видео до закрытия контекста
    const videoFile = await videoPage.video().path();
    console.log(`Запись завершена. Временный файл сохранен: ${videoFile}`);
    
    await videoContext.close();
    await browser.close();
    
    // ==========================================
    // ЭТАП 3: Конвертация видео в MP4 через FFmpeg
    // ==========================================
    console.log('\n--- Шаг 3: Конвертация WebM в универсальный MP4 (H.264)...');
    
    const outputMp4Path = path.join(VIDEO_DIR, 'presentation_reels.mp4');
    
    // Команда ffmpeg для конвертации видео с максимальным качеством и совместимостью
    const ffmpegCommand = `ffmpeg -y -i "${videoFile}" -c:v libx264 -pix_fmt yuv420p -profile:v high -level:v 4.0 -crf 22 "${outputMp4Path}"`;
    
    try {
        console.log('Запуск FFmpeg...');
        execSync(ffmpegCommand, { stdio: 'inherit' });
        console.log(`Видео успешно сконвертировано: assets/exported/video/presentation_reels.mp4`);
    } catch (error) {
        console.error('Ошибка при конвертации видео через FFmpeg:', error);
    }
    
    // Очищаем временную папку записи
    try {
        fs.rmSync(TEMP_VIDEO_DIR, { recursive: true, force: true });
        console.log('Временные файлы успешно удалены.');
    } catch (err) {
        console.error('Не удалось удалить временные файлы:', err);
    }
    
    // ==========================================
    // ЭТАП 4: Создание ZIP-архива с картинками-слайдами
    // ==========================================
    console.log('\n--- Шаг 4: Создание ZIP-архива с картинками-слайдами...');
    const zipPath = path.join(EXPORT_DIR, 'face_to_face_carousel.zip');
    
    if (fs.existsSync(zipPath)) {
        fs.unlinkSync(zipPath);
    }
    
    const zipCommand = `cd "${IMAGES_DIR}" && zip -r "${zipPath}" ./*.png`;
    
    try {
        console.log('Запуск утилиты zip...');
        execSync(zipCommand, { stdio: 'inherit' });
        console.log(`ZIP-архив успешно создан: assets/exported/face_to_face_carousel.zip`);
    } catch (error) {
        console.error('Ошибка при создании ZIP-архива:', error);
    }
    
    console.log('\n=== ЭКСПОРТ УСПЕШНО ЗАВЕРШЕН! ===');
}

run().catch(console.error);
