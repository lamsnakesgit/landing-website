---
name: notion-integration
description: Работа с Notion API для создания, чтения и обновления баз данных и страниц.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Notion Integration Skill

## Настройка
1. Создай интеграцию на [developers.notion.com](https://www.notion.so/my-integrations).
2. Получи `NOTION_TOKEN` (Internal Integration Token).
3. Поделись нужной базой/страницей с интеграцией через меню **Share**.
4. ID базы данных — 32-символьная строка из URL: `notion.so/workspace/DATABASE_ID?v=...`

## Установка
```bash
npm install @notionhq/client
```

## Инициализация
```javascript
const { Client } = require('@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_TOKEN });
```

## Работа с базами данных

### Создание записи
```javascript
async function addItem(databaseId, title, status, tags = []) {
  try {
    return await notion.pages.create({
      parent: { database_id: databaseId },
      properties: {
        Name: { title: [{ text: { content: title } }] },
        Status: { select: { name: status } },
        Tags: { multi_select: tags.map(t => ({ name: t })) },
        Created: { date: { start: new Date().toISOString() } },
      },
    });
  } catch (error) {
    console.error(`Ошибка создания записи: ${error.message}`);
    throw error;
  }
}
```

### Запрос с фильтрацией и сортировкой
```javascript
async function queryDatabase(databaseId, status, sortBy = 'created_time') {
  try {
    const response = await notion.databases.query({
      database_id: databaseId,
      filter: {
        and: [
          { property: 'Status', select: { equals: status } },
          { property: 'Created', date: { past_week: {} } },
        ]
      },
      sorts: [{ timestamp: sortBy, direction: 'descending' }],
    });
    return response.results;
  } catch (error) {
    console.error(`Ошибка запроса: ${error.message}`);
    throw error;
  }
}
```

### Обновление записи
```javascript
async function updateItem(pageId, newStatus) {
  try {
    return await notion.pages.update({
      page_id: pageId,
      properties: {
        Status: { select: { name: newStatus } },
      },
    });
  } catch (error) {
    console.error(`Ошибка обновления: ${error.message}`);
    throw error;
  }
}
```

## Пагинация (обязательна для больших баз)
```javascript
async function getAllItems(databaseId) {
  let allResults = [];
  let hasMore = true;
  let startCursor = undefined;

  while (hasMore) {
    const response = await notion.databases.query({
      database_id: databaseId,
      start_cursor: startCursor,
      page_size: 100, // Максимум 100 за запрос
    });
    allResults.push(...response.results);
    hasMore = response.has_more;
    startCursor = response.next_cursor;
  }
  return allResults;
}
```

## Работа с блоками (контент страницы)

### Чтение контента страницы
```javascript
async function getPageContent(pageId) {
  const blocks = [];
  let cursor = undefined;
  let hasMore = true;

  while (hasMore) {
    const response = await notion.blocks.children.list({
      block_id: pageId,
      start_cursor: cursor,
      page_size: 100,
    });
    blocks.push(...response.results);
    hasMore = response.has_more;
    cursor = response.next_cursor;
  }
  return blocks;
}
```

### Добавление контента на страницу
```javascript
async function appendToPage(pageId, text) {
  await notion.blocks.children.append({
    block_id: pageId,
    children: [
      {
        object: 'block',
        type: 'paragraph',
        paragraph: {
          rich_text: [{ type: 'text', text: { content: text } }],
        },
      },
    ],
  });
}
```

### Добавление heading + toggle
```javascript
async function addSection(pageId, heading, content) {
  await notion.blocks.children.append({
    block_id: pageId,
    children: [
      {
        type: 'heading_2',
        heading_2: {
          rich_text: [{ text: { content: heading } }],
        },
      },
      {
        type: 'paragraph',
        paragraph: {
          rich_text: [{ text: { content: content } }],
        },
      },
    ],
  });
}
```

## Типы свойств (Properties)

| Тип | Пример значения |
|---|---|
| `title` | `{ title: [{ text: { content: "Текст" } }] }` |
| `rich_text` | `{ rich_text: [{ text: { content: "Текст" } }] }` |
| `number` | `{ number: 42 }` |
| `select` | `{ select: { name: "Option" } }` |
| `multi_select` | `{ multi_select: [{ name: "Tag1" }, { name: "Tag2" }] }` |
| `date` | `{ date: { start: "2025-01-01" } }` |
| `checkbox` | `{ checkbox: true }` |
| `url` | `{ url: "https://example.com" }` |
| `email` | `{ email: "user@example.com" }` |
| `relation` | `{ relation: [{ id: "page-id" }] }` |

## Ограничения API
- **Rate limit**: 3 запроса в секунду (средний) / кратковременный burst допустим.
- **Пагинация**: Максимум 100 результатов за запрос.
- **Размер текста**: Максимум 2000 символов на один rich_text элемент.
- **Глубина блоков**: Максимум 2 уровня вложенности при создании.

## Лучшие практики
- 🚨 Всегда обрабатывай ошибки API (rate limit, 400, 404).
- Используй пагинацию — никогда не предполагай, что один запрос вернёт все данные.
- Для массовых операций добавляй `await sleep(350)` между запросами (rate limit).
- Кэшируй ID баз данных и страниц в env-переменных.
- Для синхронизации используй `last_edited_time` как фильтр.
