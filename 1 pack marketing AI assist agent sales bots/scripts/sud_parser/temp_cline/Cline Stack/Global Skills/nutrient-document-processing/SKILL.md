---
name: nutrient-document-processing
description: Обработка, парсинг и извлечение данных из документов (PDF, DOCX) с использованием современных библиотек.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Document Processing Skill

## Выбор инструмента

| Библиотека | Лучше для | Язык |
|---|---|---|
| **pdfplumber** | Структурированные PDF с таблицами | Python |
| **PyMuPDF (fitz)** | Высокая скорость, изображения, аннотации | Python |
| **unstructured** | RAG пайплайны, мультиформат | Python |
| **marker** | Конвертация PDF → Markdown | Python |
| **Docling** (IBM) | ML-распознавание сложных layout | Python |
| **python-docx** | Word документы (чтение/запись) | Python |
| **pytesseract** | OCR для сканов и изображений | Python |
| **pdfminer.six** | Детальный анализ текстового layout | Python |

## Извлечение текста из PDF

### pdfplumber (рекомендуется для таблиц)
```python
import pdfplumber

def extract_text(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Не удалось обработать PDF: {e}")
    return text
```

### PyMuPDF (рекомендуется для скорости)
```python
import fitz  # PyMuPDF

def extract_text_fast(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text
```

## Извлечение таблиц

### pdfplumber — точное извлечение
```python
import pdfplumber
import csv

def extract_tables(file_path: str):
    tables = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for table in page_tables:
                tables.append({
                    "page": i + 1,
                    "headers": table[0] if table else [],
                    "rows": table[1:] if len(table) > 1 else []
                })
    return tables
```

### Визуальная отладка таблиц
```python
with pdfplumber.open("doc.pdf") as pdf:
    page = pdf.pages[0]
    # Визуализация найденных линий и таблиц
    im = page.to_image(resolution=150)
    im.debug_tablefinder()
    im.save("debug_table.png")
```

## Чтение DOCX
```python
from docx import Document

def read_docx(file_path: str) -> dict:
    doc = Document(file_path)
    result = {
        "paragraphs": [p.text for p in doc.paragraphs if p.text.strip()],
        "tables": [],
        "metadata": {
            "author": doc.core_properties.author,
            "created": str(doc.core_properties.created),
            "modified": str(doc.core_properties.modified),
        }
    }
    for table in doc.tables:
        rows = []
        for row in table.rows:
            rows.append([cell.text for cell in row.cells])
        result["tables"].append(rows)
    return result
```

## OCR (Оптическое распознавание)
```python
import pytesseract
from PIL import Image

def ocr_image(image_path: str, lang: str = "rus+eng") -> str:
    image = Image.open(image_path)
    # Предобработка для улучшения OCR
    image = image.convert("L")  # Grayscale
    text = pytesseract.image_to_string(image, lang=lang)
    return text
```

### OCR для PDF-сканов
```python
import fitz
import pytesseract
from PIL import Image
import io

def ocr_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        # Извлечь изображение страницы
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text += pytesseract.image_to_string(img, lang="rus+eng") + "\n"
    doc.close()
    return text
```

## Подготовка для RAG (Retrieval-Augmented Generation)

### Чанкинг документа
```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if c]
```

### Семантический чанкинг (по заголовкам/абзацам)
```python
import re

def semantic_chunk(text: str) -> list:
    # Разбивка по заголовкам и двойным переносам строк
    sections = re.split(r'\n{2,}|(?=^#{1,3}\s)', text, flags=re.MULTILINE)
    return [s.strip() for s in sections if s.strip()]
```

### Unstructured (мультиформат, production-ready)
```python
from unstructured.partition.auto import partition

elements = partition(filename="document.pdf")
for el in elements:
    print(f"[{el.category}] {el.text[:100]}")
# Категории: Title, NarrativeText, Table, ListItem, Image, etc.
```

## Извлечение метаданных
```python
import fitz

def get_pdf_metadata(file_path: str) -> dict:
    doc = fitz.open(file_path)
    meta = doc.metadata
    return {
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "pages": doc.page_count,
        "created": meta.get("creationDate", ""),
        "encrypted": doc.is_encrypted,
    }
```

## Лучшие практики
- 🚨 Всегда оборачивай в try/catch (зашифрованные/повреждённые PDF).
- Для сканов предварительно обрабатывай изображения (контрастность, бинаризация, deskew).
- Используй `unstructured` или `Docling` для сложных документов с колонками.
- Для RAG: chunk_size 500-1500 символов, overlap 10-20%.
- Конвертируй PDF → Markdown через `marker` для LLM-обработки.
- Извлекай метаданные для фильтрации и индексации.
