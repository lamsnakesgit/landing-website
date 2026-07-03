---
name: frontend-design
description: Создание современных, адаптивных и доступных интерфейсов с использованием React, Tailwind CSS и принципов UI/UX.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Frontend Design Skill

## Технологический стек
- **Framework**: React / Next.js (App Router)
- **Styling**: Tailwind CSS v4 + CSS Variables
- **Components**: Shadcn UI (копируемые компоненты, не npm-зависимость)
- **Primitives**: Radix UI (доступность из коробки: focus traps, keyboard nav, ARIA)
- **Icons**: Lucide React
- **Анимации**: Framer Motion / tw-animate-css
- **Тестирование a11y**: @axe-core/react, @axe-core/playwright

## Инициализация проекта
```bash
npx create-next-app@latest my-app --typescript --tailwind --app
npx shadcn@latest init
# ✅ CSS variables: Yes
# ✅ Dark mode: Yes
# ✅ TypeScript strict: Yes
```

### Добавление компонентов Shadcn
```bash
npx shadcn@latest add button dialog tabs dropdown-menu
```
Компоненты копируются в проект — ты владеешь кодом, нет внешних зависимостей.

## Принципы работы

### 1. Mobile First
Всегда начинай с мобильных разрешений, расширяй для больших экранов:
```tsx
<div className="px-4 md:px-8 lg:px-16">
  <h1 className="text-xl md:text-2xl lg:text-4xl">Заголовок</h1>
</div>
```

### 2. Компонентный подход (Atomic Design)
- **Atoms**: Button, Input, Badge
- **Molecules**: SearchBar (Input + Button), Card (Image + Title + Text)
- **Organisms**: Navbar, Sidebar, DataTable
- **Templates**: Layout с Sidebar + Content area
- **Pages**: Конкретные страницы приложения

### 3. Доступность (A11y) — обязательна
Radix UI обеспечивает из коробки:
- Focus traps в модальных окнах
- Keyboard navigation (Tab, Enter, Escape, Arrow keys)
- ARIA-атрибуты автоматически

Дополнительно:
- Семантический HTML (`<nav>`, `<main>`, `<section>`, `<article>`)
- Контрастность цветов (WCAG AA: 4.5:1 для текста)
- `alt` для всех изображений
- `aria-label` для иконок-кнопок

### 4. Дизайн-система через CSS Variables
```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
  }
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
  }
}
```

### 5. Tailwind Best Practices
- Используй стандартные утилиты, избегай кастомного CSS.
- Группируй классы логически: layout → spacing → typography → colors → effects.
- Используй `cn()` (из shadcn) для условного объединения классов:
```tsx
import { cn } from "@/lib/utils";

<button className={cn(
  "px-4 py-2 rounded-lg transition-colors",
  variant === "primary" && "bg-blue-600 text-white hover:bg-blue-700",
  variant === "outline" && "border border-gray-300 hover:bg-gray-50",
  disabled && "opacity-50 cursor-not-allowed"
)}>
```

### 6. Research-backed UI guardrails

- **Native first**: сначала выбирай нативные HTML-элементы. Кастомные combobox/dialog/menu/slider делай через проверенные primitives (`Radix UI`, `shadcn/ui`) или строго по `WAI-ARIA APG`, а не через самодельную клавиатурную модель.
- **State completeness**: для product UI явно проектируй `default`, `hover`, `focus`, `active`, `disabled`, `loading`, `empty`, `no results`, `error`, `success/confirmation`, `permission`, `first-use`.
- **Forms**: всегда используй видимые labels, а не placeholder вместо label; добавляй `autocomplete`, helper text, `fieldset/legend` для связанных полей, `aria-describedby` для пояснений и inline error text рядом с полем. Не делай неожиданных submit/context changes на focus или ввод.
- **Responsive accessibility**: компонент должен корректно работать при zoom 200–400%, сохранять логичный DOM/source order, использовать `rem/em` для текста, не прятать критичные действия только в hover-состоянии и иметь удобные touch targets.
- **Feedback**: ошибки и успехи должны быть видимы текстом и визуально; для больших форм используй и summary, и локальные сообщения у полей.
- **Empty states**: пустое состояние должно заменять отсутствующий контент и вести пользователя к одному главному следующему действию, а не оставлять «пустую рамку» таблицы или перегруженный набор CTA.

## Где искать лучшие UI-кейсы и паттерны

### Приоритет источников
1. **Official docs и design systems**: `W3C/WAI`, `ARIA APG`, `web.dev`, `ui.shadcn.com`, Radix UI, USWDS, Carbon, Primer, Material.
2. **Exa**: для чистых примеров, semantic search, UI-паттернов и качественных технических материалов.
3. **Tavily**: для свежих best practices, сравнений подходов и актуальных статей.
4. **GitHub MCP / code search / repo search**: для зрелых open-source реализаций dashboard, forms, auth screens, tables, settings pages и других production patterns.

### Когда поиск обязателен
- Если нужен не абстрактный UI, а референсный экран, зрелый паттерн или готовая композиция компонентов.
- Если проект требует dashboard, сложные формы, таблицы, onboarding, empty/loading/error states или мобильные паттерны.
- Если есть сомнение в лучшем UX-решении, доступности или адаптивном поведении.

### Как искать
- Ищи не «красивый дизайн вообще», а конкретный сценарий: `dashboard filters`, `settings form`, `auth form`, `billing table`, `mobile drawer navigation`.
- Предпочитай готовые паттерны из design systems и зрелых репозиториев, а не случайные dribbble-like концепты без кода.
- Для форм отдельно проверяй labels, validation, error states, keyboard navigation и mobile behavior.
- Для custom widgets отдельно проверяй keyboard model, focus management, screen reader naming/description и соответствие APG или library docs.
- Если используешь найденный паттерн, фиксируй источник и адаптируй его под русский интерфейс, доступность и текущий стек.

## Адаптивная сетка
```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

## Чек-лист реализации
- [ ] Адаптивность: 320px, 375px, 768px, 1024px, 1440px
- [ ] Темная тема работает корректно
- [ ] Все интерактивные элементы: hover, focus, active, disabled
- [ ] Продуманы ключевые состояния: loading, empty, no results, error, success, disabled, first-use
- [ ] Keyboard navigation работает (Tab, Enter, Escape)
- [ ] DOM/source order совпадает с логикой навигации по Tab на всех брейкпоинтах
- [ ] Изображения оптимизированы (Next.js Image) с alt
- [ ] Формы: валидация, понятные ошибки на русском
- [ ] Формы: видимые labels, autocomplete, helper text и связанные descriptions/errors
- [ ] Контрастность текста ≥ 4.5:1 (WCAG AA)
- [ ] Нет горизонтального скролла на мобильных
- [ ] Zoom 200%+ не ломает layout и чтение интерфейса
- [ ] Touch targets достаточно крупные для мобильного использования
- [ ] Loading/skeleton states для асинхронных данных
- [ ] Для нетривиального UI найдены и проверены референсные кейсы или готовые паттерны

## Полезные паттерны

### Responsive Dialog → Drawer на мобильных
```tsx
import { useMediaQuery } from "@/hooks/use-media-query";

const isDesktop = useMediaQuery("(min-width: 768px)");
// Desktop → Dialog, Mobile → Drawer
```

### Оптимистичные обновления UI
Обновляй UI сразу, не дожидаясь ответа сервера. Откатывай при ошибке.
