import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const HTML_FILE = path.join(ROOT, 'public/carousels/hormozi-enhance-offer-carousel.html');
const OUT_DIR = path.join(ROOT, 'public/carousels/export/hormozi-enhance');
const TOTAL_SLIDES = 8;

const WIDTH = 1080;
const HEIGHT = 1350;

async function exportSlides() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  const fileUrl = 'file://' + HTML_FILE;
  console.log('Opening:', fileUrl);

  await page.goto(fileUrl, { waitUntil: 'networkidle' });

  // Ждём загрузку шрифтов и рендер
  await page.waitForTimeout(1500);

  for (let i = 1; i <= TOTAL_SLIDES; i++) {
    const hash = `#slide-${i}`;
    await page.goto(fileUrl + hash, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);

    const outPath = path.join(OUT_DIR, `slide-${String(i).padStart(2, '0')}.png`);
    await page.screenshot({ path: outPath, width: WIDTH, height: HEIGHT, fullPage: false });
    console.log(`✓ Saved ${outPath}`);
  }

  await browser.close();
  console.log('\nDone! All 8 slides exported to', OUT_DIR);
}

exportSlides().catch((err) => {
  console.error('Export failed:', err);
  process.exit(1);
});