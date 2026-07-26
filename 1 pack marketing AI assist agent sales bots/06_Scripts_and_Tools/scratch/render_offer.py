import os
import asyncio
from playwright.async_api import async_playwright

html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Оффер</title>
    <!-- Подключаем шрифты Montserrat и Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Montserrat:wght@700;800;900&display=swap" rel="stylesheet">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            color: #ffffff;
            background-color: #06060a;
            width: 1080px;
            height: 1920px;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }

        /* Задний фон */
        .bg-image {
            position: absolute;
            top: 0;
            left: 0;
            width: 1080px;
            height: 1920px;
            background-image: url('../assets/bg_offer.png');
            background-size: cover;
            background-position: center;
            z-index: 1;
        }

        /* Свечения */
        .glow-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 50% 20%, rgba(79, 172, 254, 0.15), transparent 60%),
                        radial-gradient(circle at 80% 80%, rgba(0, 242, 254, 0.1), transparent 50%),
                        linear-gradient(180deg, rgba(6, 6, 10, 0.4) 0%, rgba(6, 6, 10, 0.85) 100%);
            z-index: 2;
        }

        /* Контейнер */
        .container {
            position: relative;
            z-index: 3;
            width: 960px;
            height: 1800px;
            padding: 70px 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: rgba(10, 10, 18, 0.65);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        /* Декоративная рамка с подсветкой */
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 40px;
            padding: 2px;
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.4), rgba(0, 242, 254, 0.1) 40%, rgba(0, 242, 254, 0.1) 60%, rgba(162, 89, 255, 0.4));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
        }

        /* Хедер */
        .header {
            display: flex;
            flex-direction: column;
            gap: 25px;
        }

        .badge {
            align-self: flex-start;
            padding: 10px 24px;
            background: linear-gradient(90deg, rgba(79, 172, 254, 0.2) 0%, rgba(0, 242, 254, 0.2) 100%);
            border: 1px solid rgba(0, 242, 254, 0.3);
            border-radius: 50px;
            font-family: 'Montserrat', sans-serif;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 2px;
            color: #00f2fe;
            text-transform: uppercase;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.15);
        }

        .title {
            font-family: 'Montserrat', sans-serif;
            font-size: 54px;
            font-weight: 900;
            line-height: 1.2;
            background: linear-gradient(135deg, #ffffff 0%, #a2a2bd 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Проблема */
        .pain-point {
            margin-top: 15px;
            padding: 30px;
            background: rgba(255, 79, 79, 0.05);
            border-left: 5px solid #ff4f4f;
            border-radius: 0 20px 20px 0;
        }

        .pain-point p {
            font-size: 26px;
            line-height: 1.5;
            color: #ffcccc;
            font-weight: 400;
        }

        .pain-point span {
            color: #ff4f4f;
            font-weight: 600;
        }

        /* Оффер интро */
        .offer-intro {
            font-family: 'Montserrat', sans-serif;
            font-size: 34px;
            font-weight: 800;
            line-height: 1.3;
            color: #ffffff;
            margin-top: 25px;
        }

        .offer-intro span {
            background: linear-gradient(90deg, #00f2fe, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Особенности / Фичи */
        .features-list {
            display: flex;
            flex-direction: column;
            gap: 25px;
            margin-top: 20px;
            margin-bottom: 20px;
        }

        .feature-card {
            display: flex;
            align-items: flex-start;
            gap: 25px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            transition: all 0.3s ease;
        }

        .feature-icon {
            width: 70px;
            height: 70px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.15), rgba(0, 242, 254, 0.15));
            border: 1px solid rgba(0, 242, 254, 0.25);
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
        }

        .feature-icon svg {
            width: 35px;
            height: 35px;
            fill: none;
            stroke: #00f2fe;
            stroke-width: 2;
        }

        .feature-content {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .feature-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
        }

        .feature-desc {
            font-size: 24px;
            line-height: 1.4;
            color: #b0b0cc;
            font-weight: 300;
        }

        /* Футер */
        .footer {
            display: flex;
            flex-direction: column;
            gap: 35px;
            align-items: center;
            text-align: center;
        }

        .footer-tagline {
            font-family: 'Montserrat', sans-serif;
            font-size: 28px;
            font-weight: 800;
            color: #00f2fe;
            text-shadow: 0 0 15px rgba(0, 242, 254, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .cta-button {
            width: 100%;
            padding: 30px 40px;
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            border: none;
            border-radius: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 15px 35px rgba(0, 242, 254, 0.3);
            position: relative;
            overflow: hidden;
        }

        .cta-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -50%;
            width: 200%;
            height: 100%;
            background: linear-gradient(to right, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.3) 50%, rgba(255, 255, 255, 0) 100%);
            transform: skewX(-25deg);
            animation: shine 4s infinite;
        }

        @keyframes shine {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        .cta-text {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
            text-align: left;
        }

        .cta-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #030a16;
        }

        .cta-subtitle {
            font-size: 20px;
            color: rgba(3, 10, 22, 0.7);
            font-weight: 500;
        }

        .cta-contact {
            background: rgba(3, 10, 22, 0.15);
            padding: 12px 28px;
            border-radius: 18px;
            font-family: 'Montserrat', sans-serif;
            font-size: 32px;
            font-weight: 900;
            color: #030a16;
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            gap: 10px;
        }
    </style>
</head>
<body>
    <div class="bg-image"></div>
    <div class="glow-overlay"></div>
    
    <div class="container">
        <!-- Шапка -->
        <div class="header">
            <div class="badge">AI Маркетинг</div>
            <h1 class="title">Реклама «жрёт» бюджет,<br>а прибыли нет?</h1>
            
            <div class="pain-point">
                <p>Если у вас уже есть поток заявок, но реклама не даёт стабильной прибыли — скорее всего, проблема <span>не в трафике, а в системе.</span></p>
            </div>
            
            <div class="offer-intro">
                Мы внедряем <span>AI-систему продаж</span>, которая:
            </div>
        </div>

        <!-- Список преимуществ -->
        <div class="features-list">
            <!-- 1 -->
            <div class="feature-card">
                <div class="feature-icon">
                    <svg viewBox="0 0 24 24">
                        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="feature-content">
                    <h3 class="feature-title">Снижает стоимость лида</h3>
                    <p class="feature-desc">За счет автоматической оптимизации рекламных кампаний и умного управления бюджетом.</p>
                </div>
            </div>

            <!-- 2 -->
            <div class="feature-card">
                <div class="feature-icon">
                    <svg viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M12 6v6l4 2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="feature-content">
                    <h3 class="feature-title">Заменяет ручного таргетолога</h3>
                    <p class="feature-desc">Контроль показателей 24/7 и непрерывный тест рекламных гипотез без выходных.</p>
                </div>
            </div>

            <!-- 3 -->
            <div class="feature-card">
                <div class="feature-icon">
                    <svg viewBox="0 0 24 24">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="feature-content">
                    <h3 class="feature-title">AI-ассистенты на связи</h3>
                    <p class="feature-desc">Обрабатывают заявки мгновенно, общаются как живой человек и разгружают ваш отдел продаж.</p>
                </div>
            </div>

            <!-- 4 -->
            <div class="feature-card">
                <div class="feature-icon">
                    <svg viewBox="0 0 24 24">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke-linecap="round" stroke-linejoin="round"/>
                        <polyline points="22 4 12 14.01 9 11.01" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="feature-content">
                    <h3 class="feature-title">Дожимает до сделки</h3>
                    <p class="feature-desc">Автоматически доводит клиентов до оплаты и делает регулярные повторные продажи.</p>
                </div>
            </div>
        </div>

        <!-- Футер -->
        <div class="footer">
            <div class="footer-tagline">Без человеческого фактора и сливов бюджета</div>
            
            <div class="cta-button">
                <div class="cta-text">
                    <span class="cta-title">Покажу, как это внедрить под вас</span>
                    <span class="cta-subtitle">Напишите мне в личные сообщения</span>
                </div>
                <div class="cta-contact">
                    <!-- Иконка телеграма -->
                    <svg style="width: 32px; height: 32px; fill: #030a16;" viewBox="0 0 24 24">
                        <path d="M12 .587c-6.29 0-11.39 5.099-11.39 11.388 0 6.29 5.1 11.388 11.39 11.388 6.29 0 11.39-5.099 11.39-11.388 0-6.29-5.1-11.388-11.39-11.388zm5.28 7.39l-1.88 8.875c-.14.637-.518.795-1.05.495l-2.875-2.12-1.387 1.336c-.154.154-.283.283-.58.283l.206-2.924 5.323-4.81c.231-.206-.05-.32-.36-.114l-6.58 4.14-2.834-.887c-.615-.19-.628-.615.128-.91l11.083-4.27c.513-.19.96.115.772.937z"/>
                    </svg>
                    @nnsvt
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

async def capture():
    # Создаем временный файл шаблона
    template_path = os.path.abspath("scratch/offer_template.html")
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Запись шаблона в {template_path}...")
    
    async with async_playwright() as p:
        print("Запуск браузера Playwright...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=2 # Для Retina качества
        )
        page = await context.new_page()
        
        # Переходим к локальному файлу
        file_url = f"file://{template_path}"
        print(f"Открытие страницы: {file_url}...")
        await page.goto(file_url)
        
        # Ждем загрузки шрифтов и рендеринга
        await page.wait_for_timeout(2000)
        
        output_path = os.path.abspath("assets/offer_creative.png")
        print(f"Снимок экрана... Сохранение в {output_path}")
        await page.screenshot(path=output_path, type="png")
        
        await browser.close()
        print("Рендеринг завершен!")

if __name__ == "__main__":
    asyncio.run(capture())
