import argparse
import asyncio
import csv
import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError, async_playwright

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SudParser")

BASE_URL = "https://office.sud.kz"
COURT_ACTS_URL = f"{BASE_URL}/courtActs/index.xhtml"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD_DIR = PROJECT_ROOT / "downloads" / "cases"
OUTPUT_DIR = PROJECT_ROOT / "data" / "court_acts"
CABINET_OUTPUT_DIR = PROJECT_ROOT / "data" / "cabinet"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CABINET_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Коды категорий из формы банка судебных актов office.sud.kz.
LABOR_CATEGORY_CODES = {
    "labor_disputes": "142030000100000000",
    "reinstatement": "142030000100010000",
    "reinstatement_with_salary": "142030000100010010",
    "salary_payments": "142030000100020000",
    "salary_and_vacation_compensation": "142030000100020010",
}

INSTANCE_VALUES = {
    "first": "FIRSTINSTANCE",
    "appeal": "APPEAL",
    "cassation": "CASSATION",
    "supreme": "SUPERVISION",
}

CASE_RESULT_VALUES = {
    "satisfied": "62012001",
    "partly_satisfied": "62012002",
    "rejected": "62012003",
    "court_order": "62012004",
}


@dataclass
class CourtActsSearchConfig:
    """Параметры поиска судебных актов по трудовым спорам."""

    year: str = "2025"
    category_code: str = LABOR_CATEGORY_CODES["labor_disputes"]
    keyword: str = "Еңбек даулары"
    district_code: str = ""
    court_code: str = ""
    iin_or_bin: str = ""
    plaintiff: str = ""
    defendant: str = ""
    attorney: str = ""
    case_result: str = ""
    instances: List[str] = field(default_factory=lambda: [INSTANCE_VALUES["first"]])
    manual_captcha_wait_seconds: int = 180
    max_results: int = 50
    download_pdfs: bool = False
    headless: bool = False
    browser_channel: str = ""
    user_data_dir: str = ""
    storage_state_path: str = ""
    cookies_json_path: str = ""


@dataclass
class CourtActResult:
    """Нормализованная карточка найденного судебного акта."""

    row_index: int
    case_number: str = ""
    court: str = ""
    category: str = ""
    parties: str = ""
    judge: str = ""
    result: str = ""
    date: str = ""
    text: str = ""
    links: List[str] = field(default_factory=list)
    pdf_files: List[str] = field(default_factory=list)


async def is_probably_logged_in(page: Page) -> bool:
    """Эвристика: проверяем, выглядит ли страница как уже авторизованный кабинет."""
    auth_markers = [
        "text=Выход",
        "text=Шығу",
        "text=Личный кабинет",
        "text=Жеке кабинет",
        "a[href*='logout']",
        "a[href*='profile']",
    ]
    for selector in auth_markers:
        try:
            if await page.locator(selector).first.is_visible(timeout=1000):
                return True
        except Exception:
            continue

    # На office.sud.kz часть элементов может быть невидимой/скрытой в headless,
    # поэтому дополнительно проверяем HTML: это не раскрывает cookies и надёжнее для smoke-теста.
    html = await page.content()
    html_markers = ["Выход", "Шығу", "logout", "Жеке кабинет", "Личный кабинет"]
    login_markers = ["tab-eds", "selectSignType", "Авторизация", "Войти", "Кіру"]
    has_auth_marker = any(marker in html for marker in html_markers)
    has_login_marker = any(marker in html for marker in login_markers)

    return has_auth_marker and not has_login_marker


async def login_via_ncalayer(page: Page):
    """
    Функция для прохождения авторизации ЭЦП.
    Предполагается, что на фоне запущен ncalayer_mock.py на порту 13579.
    """
    logger.info("Попытка нажать на вкладку ЭЦП и кнопку входа...")

    try:
        eds_tab = page.locator("div#tab-eds")
        if await eds_tab.is_visible():
            await eds_tab.click()
            logger.info("Открыта вкладка ЭЦП арқылы кіру.")
            await page.wait_for_timeout(1000)

            select_cert_btn = page.locator("input[onclick*='selectSignType()']")
            if await select_cert_btn.is_visible():
                await select_cert_btn.click()
                logger.info("Кликнули 'Выбрать сертификат'. Запрос отправлен в NCALayer/mock.")
                await page.wait_for_timeout(3000)
            else:
                logger.warning("Кнопка выбора сертификата не найдена.")
        else:
            logger.warning("Вкладка ЭЦП (div#tab-eds) не найдена на главной странице.")

    except Exception as e:
        logger.error(f"Ошибка при попытке входа: {e}")


async def search_cases_by_iin(page: Page, iin: str):
    """Поиск судебных дел по ИИН/БИН в авторизованном разделе `/form/lawsuit/`."""
    logger.info(f"Начинаем поиск дел для ИИН/БИН: {'<set>' if iin else '<empty>'}")

    try:
        if "/form/lawsuit" not in page.url:
            await page.goto(f"{BASE_URL}/form/lawsuit/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

        (CABINET_OUTPUT_DIR / "lawsuit_search_before.html").write_text(await page.content(), encoding="utf-8")

        search_input = page.locator("#j_idt36\\:j_idt37\\:edit-iin")
        if await search_input.count() == 0:
            search_input = page.locator("input[id$='edit-iin'], input[name$='edit-iin']").first

        if await search_input.count() > 0 and await search_input.first.is_visible(timeout=5000):
            await search_input.first.fill(iin)
            logger.info("ИИН/БИН введен.")

            search_button = page.locator(
                "input[type='submit'][value*='Поиск'], input[type='submit'][value*='Іздеу'], "
                "button:has-text('Поиск'), button:has-text('Іздеу'), a:has-text('Поиск'), a:has-text('Іздеу')"
            ).first

            if await search_button.count() > 0:
                await search_button.click()
                logger.info("Нажали кнопку поиска судебных дел.")
                await page.wait_for_timeout(7000)
            else:
                logger.warning("Кнопка поиска не найдена; сохраняю HTML для диагностики.")
        else:
            logger.warning("Поле ИИН/БИН не найдено на странице поиска судебных дел.")

        (CABINET_OUTPUT_DIR / "lawsuit_search_after.html").write_text(await page.content(), encoding="utf-8")
        await page.screenshot(path=str(CABINET_OUTPUT_DIR / "lawsuit_search_after.png"), full_page=True)

    except Exception as e:
        logger.error(f"Ошибка при поиске по ИИН/БИН: {e}")


def extract_search_form_metadata(html: str) -> Dict[str, object]:
    """
    Извлекает карту полей и справочники из HTML формы банка судебных актов.
    Это нужно, чтобы не угадывать JSF id и коды категорий.
    """
    soup = BeautifulSoup(html, "html.parser")
    main_form = soup.find("form", id="j_idt43") or soup.find("form")
    if not main_form:
        raise ValueError("Основная форма поиска не найдена")

    fields = []
    for tag in main_form.find_all(["input", "select", "textarea"]):
        label = ""
        tag_id = tag.get("id")
        if tag_id:
            label_tag = soup.find("label", attrs={"for": tag_id})
            if label_tag:
                label = label_tag.get_text(" ", strip=True)

        options = []
        if tag.name == "select":
            options = [
                {"value": option.get("value", ""), "text": option.get_text(" ", strip=True)}
                for option in tag.find_all("option")
            ]

        fields.append(
            {
                "tag": tag.name,
                "id": tag_id,
                "name": tag.get("name", ""),
                "type": tag.get("type", ""),
                "label": label,
                "value": tag.get("value", ""),
                "options": options,
            }
        )

    return {
        "form_id": main_form.get("id"),
        "form_action": main_form.get("action"),
        "fields": fields,
        "labor_categories": [
            option
            for field in fields
            if field["id"] == "j_idt43:edit-category"
            for option in field["options"]
            if "Еңбек" in option["text"] or "жалақы" in option["text"].lower()
        ],
    }


def save_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def save_results_csv(path: Path, results: List[CourtActResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "row_index",
        "case_number",
        "court",
        "category",
        "parties",
        "judge",
        "result",
        "date",
        "text",
        "links",
        "pdf_files",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in results:
            row = asdict(item)
            row["links"] = " | ".join(item.links)
            row["pdf_files"] = " | ".join(item.pdf_files)
            writer.writerow(row)


def normalize_cookie_for_playwright(cookie: Dict[str, object]) -> Dict[str, object]:
    """Приводит экспортированную cookie к формату Playwright без раскрытия значения."""
    normalized = dict(cookie)

    same_site = normalized.get("sameSite")
    same_site_map = {
        "no_restriction": "None",
        "unspecified": "Lax",
        "lax": "Lax",
        "strict": "Strict",
        "none": "None",
    }
    if isinstance(same_site, str):
        normalized["sameSite"] = same_site_map.get(same_site.lower(), same_site)

    if "expirationDate" in normalized and "expires" not in normalized:
        normalized["expires"] = normalized.pop("expirationDate")

    if normalized.get("expires") in (None, ""):
        normalized.pop("expires", None)

    return normalized


def load_storage_state_from_cookie_json(path: str) -> Optional[Dict[str, object]]:
    """
    Загружает cookies JSON, экспортированный из браузера, и превращает его в
    Playwright storage_state. Значения cookies не логируются.
    """
    if not path or not Path(path).exists():
        return None

    raw_data = json.loads(Path(path).read_text(encoding="utf-8"))
    cookies = raw_data.get("cookies") if isinstance(raw_data, dict) else raw_data
    if not isinstance(cookies, list):
        raise ValueError("Cookies JSON должен быть списком cookies или объектом с ключом 'cookies'.")

    normalized_cookies = [
        normalize_cookie_for_playwright(cookie)
        for cookie in cookies
        if isinstance(cookie, dict) and cookie.get("name") and cookie.get("value")
    ]

    logger.info(
        "Загружены cookies из JSON: count=%s domains=%s names=%s",
        len(normalized_cookies),
        sorted({str(cookie.get("domain", "")) for cookie in normalized_cookies}),
        sorted({str(cookie.get("name", "")) for cookie in normalized_cookies}),
    )

    return {"cookies": normalized_cookies, "origins": []}


async def select_if_present(page: Page, selector: str, value: str) -> None:
    if not value:
        return
    locator = page.locator(selector)
    if await locator.count() > 0:
        # На office.sud.kz часть select скрывается плагином selectize.
        # Playwright select_option требует видимый элемент, поэтому выставляем значение через DOM.
        await page.evaluate(
            """({ selector, value }) => {
                const element = document.querySelector(selector);
                if (!element) return false;
                element.value = value;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                if (window.$) {
                    window.$(element).val(value).trigger('change');
                }
                return true;
            }""",
            {"selector": selector, "value": value},
        )
        await page.wait_for_timeout(500)


async def fill_if_present(page: Page, selector: str, value: str) -> None:
    if not value:
        return
    locator = page.locator(selector)
    if await locator.count() > 0:
        await locator.fill(value)
        await page.wait_for_timeout(250)


async def check_instance(page: Page, value: str) -> None:
    selector = f"input[name='j_idt43:edit-participantTypeCheckbox'][value='{value}']"
    checkbox = page.locator(selector)
    if await checkbox.count() > 0:
        await page.evaluate(
            """({ selector }) => {
                const element = document.querySelector(selector);
                if (!element) return false;
                if (!element.checked) {
                    element.checked = true;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    if (window.$) {
                        window.$(element).trigger('change');
                    }
                }
                return true;
            }""",
            {"selector": selector},
        )


async def fill_court_acts_search_form(page: Page, config: CourtActsSearchConfig) -> None:
    """Заполняет форму поиска актов по трудовым спорам."""
    logger.info("Заполняем форму банка судебных актов.")

    await select_if_present(page, "#j_idt43\\:edit-period", config.year)
    await select_if_present(page, "#j_idt43\\:edit-category", config.category_code)
    await select_if_present(page, "#j_idt43\\:edit-district", config.district_code)
    await select_if_present(page, "#j_idt43\\:edit-court", config.court_code)
    await select_if_present(page, "#j_idt43\\:edit-consideration", config.case_result)

    for instance in config.instances:
        await check_instance(page, instance)

    await fill_if_present(page, "#j_idt43\\:edit-participant", config.keyword)
    await fill_if_present(page, "#j_idt43\\:iinOrBin", config.iin_or_bin)
    await fill_if_present(page, "#j_idt43\\:plaintff", config.plaintiff)
    await fill_if_present(page, "#j_idt43\\:defendant", config.defendant)
    await fill_if_present(page, "#j_idt43\\:attorney", config.attorney)


async def wait_for_manual_captcha_and_search(page: Page, wait_seconds: int) -> None:
    """
    Не обходит reCAPTCHA. Открывает браузер и даёт человеку пройти проверку
    и нажать кнопку поиска на сайте.

    Ждём не просто любой table на странице, потому что стартовая страница уже
    содержит служебные таблицы/блоки. Условие успеха — появление строк, похожих
    на судебные акты, либо изменение URL/DOM после ручного поиска.
    """
    logger.info("")
    logger.info("На странице есть Google reCAPTCHA.")
    logger.info("Я не обхожу защиту сайта. Открыл браузер для ручного действия.")
    logger.info("Действие: решите reCAPTCHA и нажмите кнопку поиска на странице.")
    logger.info(f"Скрипт будет держать браузер открытым и проверять результаты до {wait_seconds} секунд.")

    start_url = page.url
    start_html = await page.content()
    loop = asyncio.get_running_loop()
    deadline = loop.time() + wait_seconds
    last_log_second = -1

    while loop.time() < deadline:
        current_html = await page.content()
        parsed_results = parse_results_from_html(current_html, max_results=1)

        if parsed_results:
            logger.info("Похоже, результаты поиска появились на странице.")
            return

        if page.url != start_url and current_html != start_html:
            logger.info("Страница изменилась после ручного действия. Перехожу к сохранению HTML и парсингу.")
            return

        seconds_left = int(deadline - loop.time())
        if seconds_left // 30 != last_log_second // 30:
            logger.info(f"Ожидаю ручную reCAPTCHA/поиск. Осталось примерно {seconds_left} сек.")
            last_log_second = seconds_left

        await page.wait_for_timeout(2000)

    logger.warning("Время ожидания ручного поиска истекло. Сохраняю текущую страницу для диагностики.")


def normalize_spaces(value: str) -> str:
    return re.sub(r"\\s+", " ", value or "").strip()


def detect_case_number(text: str) -> str:
    patterns = [
        r"№\\s*[-А-Яа-яA-Za-z0-9/_.]+",
        r"\\b\\d{4}-\\d{2}-\\d{2}[-/][\\d/-]+\\b",
        r"\\b\\d{2,}-\\d{2,}-\\d{2,}\\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return ""


def is_court_act_link(href: str) -> bool:
    """Отсекает служебные PDF/справку и оставляет ссылки, похожие на судебные акты."""
    href_lower = (href or "").lower()
    blocked_prefixes = ("/content/files/", "/materials/", "mailto:")
    if href_lower.startswith(blocked_prefixes) or any(prefix in href_lower for prefix in blocked_prefixes):
        return False

    return (
        "courtacts" in href_lower
        or "download" in href_lower
        or "document" in href_lower
        or "view" in href_lower and "act" in href_lower
    )


def looks_like_court_act_row(text: str, links: List[str]) -> bool:
    """Проверяет, что строка похожа на результат поиска, а не на footer/help блока."""
    text_lower = normalize_spaces(text).lower()

    service_markers = [
        "көмек техникалық қолдау",
        "пайдалы сілтемелер",
        "кері байланыс",
        "iphone қолданбасын",
        "android қолданбасын",
        "құпиялылық саясаты",
    ]
    if any(marker in text_lower for marker in service_markers):
        return False

    has_relevant_link = any(is_court_act_link(link) for link in links)
    has_case_number = bool(detect_case_number(text))
    has_date = bool(re.search(r"\d{2}\.\d{2}\.\d{4}", text))
    has_legal_marker = any(
        marker in text_lower
        for marker in ["еңбек", "жалақы", "талап", "шешім", "қаулы", "үкім", "судья", "сот акт"]
    )

    return has_relevant_link or has_case_number or (has_date and has_legal_marker)


def parse_results_from_html(html: str, base_url: str = BASE_URL, max_results: int = 50) -> List[CourtActResult]:
    """
    Универсально вытаскивает строки результатов из HTML после поиска.
    JSF-разметка сайта может меняться, поэтому парсер не завязан на один класс таблицы.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: List[CourtActResult] = []

    candidate_rows = []
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) > 1:
            candidate_rows.extend(rows[1:])

    if not candidate_rows:
        # Fallback: ищем контейнеры с ссылками на судебные акты.
        candidate_rows = [
            link.parent
            for link in soup.find_all("a", href=True)
            if is_court_act_link(link["href"])
        ]

    seen_texts = set()
    for index, row in enumerate(candidate_rows, start=1):
        if len(results) >= max_results:
            break

        text = normalize_spaces(row.get_text(" ", strip=True))
        if not text or text in seen_texts:
            continue
        seen_texts.add(text)

        links = []
        for link in row.find_all("a", href=True):
            href = link["href"]
            if href.startswith("#") or not is_court_act_link(href):
                continue
            links.append(urljoin(base_url, href))

        if not looks_like_court_act_row(text, links):
            continue

        cells = [normalize_spaces(cell.get_text(" ", strip=True)) for cell in row.find_all(["td", "th"])]
        result = CourtActResult(row_index=len(results) + 1, text=text, links=links)

        if cells:
            result.case_number = detect_case_number(" ".join(cells))
            result.court = next((cell for cell in cells if "сот" in cell.lower()), "")
            result.category = next((cell for cell in cells if "еңбек" in cell.lower() or "жалақы" in cell.lower()), "")
            result.date = next((cell for cell in cells if re.search(r"\\d{2}\\.\\d{2}\\.\\d{4}", cell)), "")
            result.result = next(
                (
                    cell
                    for cell in cells
                    if any(word in cell.lower() for word in ["қанағат", "бас тарт", "қаралды", "шешім", "қаулы"])
                ),
                "",
            )
        else:
            result.case_number = detect_case_number(text)

        results.append(result)

    return results


async def download_result_pdfs(page: Page, results: List[CourtActResult]) -> None:
    """Скачивает PDF/документы из ссылок результатов, если сайт отдаёт файлы напрямую."""
    for item in results:
        for link in item.links:
            if not (".pdf" in link.lower() or "download" in link.lower() or "document" in link.lower()):
                continue

            try:
                async with page.expect_download(timeout=15000) as download_info:
                    await page.goto(link)
                download = await download_info.value
                safe_name = re.sub(r"[^0-9A-Za-zА-Яа-я_.-]+", "_", download.suggested_filename)
                target = DOWNLOAD_DIR / f"{item.row_index}_{safe_name}"
                await download.save_as(str(target))
                item.pdf_files.append(str(target))
                logger.info(f"Скачан файл: {target}")
            except Exception as error:
                logger.warning(f"Не удалось скачать {link}: {error}")


async def run_court_acts_search(config: CourtActsSearchConfig) -> List[CourtActResult]:
    """
    Запускает поиск в банке судебных актов.

    Важно: сайт защищён reCAPTCHA. Скрипт не обходит её, а готовит форму
    и ждёт ручного прохождения проверки в открытом браузере.
    """
    logger.info("Запуск поиска судебных актов по трудовым спорам.")
    logger.info(f"URL: {COURT_ACTS_URL}")
    logger.info(f"Параметры: {config}")

    async with async_playwright() as p:
        launch_kwargs = {
            "headless": config.headless,
            "viewport": {"width": 1365, "height": 900},
            "accept_downloads": True,
            "locale": "ru-RU",
        }
        if config.browser_channel:
            # Для ручной reCAPTCHA удобнее открывать обычный установленный браузер.
            launch_kwargs["channel"] = config.browser_channel

        storage_state = load_storage_state_from_cookie_json(config.cookies_json_path)
        if config.storage_state_path and Path(config.storage_state_path).exists():
            storage_state = config.storage_state_path
            logger.info(f"Загружаем storage_state: {storage_state}")

        if config.user_data_dir:
            logger.info(f"Запускаем persistent context: {config.user_data_dir}")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=config.user_data_dir,
                **launch_kwargs,
            )
            page = context.pages[0] if context.pages else await context.new_page()
        else:
            browser = await p.chromium.launch(
                headless=config.headless,
                channel=config.browser_channel or None,
            )
            context = await browser.new_context(
                viewport={"width": 1365, "height": 900},
                accept_downloads=True,
                locale="ru-RU",
                storage_state=storage_state,
            )
            page = await context.new_page()

        response = await page.goto(COURT_ACTS_URL, timeout=60000, wait_until="domcontentloaded")
        status = response.status if response else "unknown"
        logger.info(f"Статус страницы: {status}")

        await page.wait_for_timeout(5000)

        html_before = await page.content()
        save_json(OUTPUT_DIR / "court_acts_form_metadata.json", extract_search_form_metadata(html_before))
        (OUTPUT_DIR / "court_acts_form_snapshot.html").write_text(html_before, encoding="utf-8")

        await fill_court_acts_search_form(page, config)
        await page.screenshot(path=str(OUTPUT_DIR / "court_acts_filled_form.png"), full_page=True)

        if config.headless:
            logger.warning("Headless-режим не подходит для ручного прохождения reCAPTCHA.")
        else:
            await wait_for_manual_captcha_and_search(page, config.manual_captcha_wait_seconds)

        html_after = await page.content()
        (OUTPUT_DIR / "court_acts_search_results.html").write_text(html_after, encoding="utf-8")
        await page.screenshot(path=str(OUTPUT_DIR / "court_acts_search_results.png"), full_page=True)

        results = parse_results_from_html(html_after, max_results=config.max_results)

        if config.download_pdfs and results:
            await download_result_pdfs(page, results)

        save_json(OUTPUT_DIR / "court_acts_results.json", [asdict(item) for item in results])
        save_results_csv(OUTPUT_DIR / "court_acts_results.csv", results)

        if config.storage_state_path:
            await context.storage_state(path=config.storage_state_path)
            logger.info(f"Сохранили storage_state: {config.storage_state_path}")

        logger.info(f"Найдено/извлечено строк результатов: {len(results)}")
        logger.info(f"JSON: {OUTPUT_DIR / 'court_acts_results.json'}")
        logger.info(f"CSV: {OUTPUT_DIR / 'court_acts_results.csv'}")

        await context.close()
        return results


async def run_parser(
    iin_to_search: str,
    browser_channel: str = "",
    user_data_dir: str = "",
    storage_state_path: str = "",
    cookies_json_path: str = "",
    headless: bool = False,
):
    """
    Сценарий Судебного кабинета.

    Может работать через persistent profile / storage_state / cookies JSON,
    чтобы после ручной авторизации через ЭЦП или reCAPTCHA переиспользовать
    cookies/localStorage.
    """
    logger.info("Запуск парсера Судебного кабинета...")

    async with async_playwright() as p:
        storage_state = load_storage_state_from_cookie_json(cookies_json_path)
        if storage_state_path and Path(storage_state_path).exists():
            storage_state = storage_state_path
            logger.info(f"Загружаем storage_state кабинета: {storage_state}")

        if user_data_dir:
            logger.info(f"Запускаем persistent context кабинета: {user_data_dir}")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                channel=browser_channel or None,
                viewport={"width": 1280, "height": 800},
                accept_downloads=True,
                locale="ru-RU",
            )
            page = context.pages[0] if context.pages else await context.new_page()
        else:
            browser = await p.chromium.launch(headless=headless, channel=browser_channel or None)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                accept_downloads=True,
                locale="ru-RU",
                storage_state=storage_state,
            )
            page = await context.new_page()

        logger.info("Открываем https://office.sud.kz/")
        await page.goto("https://office.sud.kz/", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        html_before_login = await page.content()
        (CABINET_OUTPUT_DIR / "cabinet_homepage_before_login.html").write_text(html_before_login, encoding="utf-8")

        if await is_probably_logged_in(page):
            logger.info("Похоже, cookies/session уже открыли авторизованный кабинет. Пропускаю ЭЦП-вход.")
        else:
            logger.info("Авторизованный кабинет не обнаружен. Пробую сценарий ЭЦП/NCALayer.")
            await login_via_ncalayer(page)

        html_after_login = await page.content()
        (CABINET_OUTPUT_DIR / "cabinet_homepage_after_login.html").write_text(html_after_login, encoding="utf-8")
        await page.screenshot(path=str(CABINET_OUTPUT_DIR / "cabinet_homepage.png"), full_page=True)

        if iin_to_search:
            await search_cases_by_iin(page, iin_to_search)
        else:
            await page.goto(f"{BASE_URL}/form/lawsuit/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            (CABINET_OUTPUT_DIR / "lawsuit_search.html").write_text(await page.content(), encoding="utf-8")
            await page.screenshot(path=str(CABINET_OUTPUT_DIR / "lawsuit_search.png"), full_page=True)
            logger.info("Сохранили страницу поиска судебных дел без запуска поиска.")

        if storage_state_path:
            await context.storage_state(path=storage_state_path)
            logger.info(f"Сохранили storage_state кабинета: {storage_state_path}")

        if headless:
            logger.info("Парсер завершил базовый сценарий в headless-режиме.")
        else:
            logger.info("Парсер завершил базовый сценарий. Оставляем браузер открытым на 30 секунд.")
            await page.wait_for_timeout(30000)

        await context.close()
        logger.info("Браузер закрыт.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Парсер банка судебных актов office.sud.kz")
    parser.add_argument("--mode", choices=["court-acts", "iin"], default="court-acts")
    parser.add_argument("--iin", default="", help="ИИН/БИН для старого сценария поиска")
    parser.add_argument("--year", default="2025", help="Есептік жыл / год поиска")
    parser.add_argument(
        "--category",
        default="labor_disputes",
        choices=list(LABOR_CATEGORY_CODES.keys()),
        help="Категория трудового спора",
    )
    parser.add_argument("--keyword", default="Еңбек даулары", help="Ключевая фраза для поиска")
    parser.add_argument("--district", default="", help="Код области из формы")
    parser.add_argument("--court", default="", help="Код суда из формы")
    parser.add_argument("--plaintiff", default="", help="Истец")
    parser.add_argument("--defendant", default="", help="Ответчик")
    parser.add_argument("--attorney", default="", help="Адвокат")
    parser.add_argument("--case-result", default="", choices=["", *CASE_RESULT_VALUES.keys()])
    parser.add_argument("--instances", default="first", help="Инстанции через запятую: first,appeal,cassation,supreme")
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument("--manual-captcha-wait", type=int, default=180)
    parser.add_argument("--download-pdfs", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--browser-channel",
        default="",
        help="Канал Playwright для GUI-браузера, например chrome для установленного Google Chrome",
    )
    parser.add_argument(
        "--user-data-dir",
        default="",
        help="Папка persistent Chrome-профиля для переиспользования cookies/localStorage между запусками",
    )
    parser.add_argument(
        "--storage-state",
        default="",
        help="JSON-файл Playwright storage_state для сохранения/загрузки cookies/localStorage",
    )
    parser.add_argument(
        "--cookies-json",
        default="",
        help="JSON-файл с экспортированными cookies браузера, например sud_cookies.json",
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> CourtActsSearchConfig:
    instances = []
    for item in args.instances.split(","):
        key = item.strip()
        if key:
            instances.append(INSTANCE_VALUES[key])

    return CourtActsSearchConfig(
        year=args.year,
        category_code=LABOR_CATEGORY_CODES[args.category],
        keyword=args.keyword,
        district_code=args.district,
        court_code=args.court,
        plaintiff=args.plaintiff,
        defendant=args.defendant,
        attorney=args.attorney,
        case_result=CASE_RESULT_VALUES.get(args.case_result, ""),
        instances=instances or [INSTANCE_VALUES["first"]],
        manual_captcha_wait_seconds=args.manual_captcha_wait,
        max_results=args.max_results,
        download_pdfs=args.download_pdfs,
        headless=args.headless,
        browser_channel=args.browser_channel,
        user_data_dir=args.user_data_dir,
        storage_state_path=args.storage_state,
        cookies_json_path=args.cookies_json,
    )


if __name__ == "__main__":
    cli_args = parse_args()

    if cli_args.mode == "iin":
        asyncio.run(
            run_parser(
                cli_args.iin,
                browser_channel=cli_args.browser_channel,
                user_data_dir=cli_args.user_data_dir,
                storage_state_path=cli_args.storage_state,
                cookies_json_path=cli_args.cookies_json,
                headless=cli_args.headless,
            )
        )
    else:
        asyncio.run(run_court_acts_search(build_config(cli_args)))
