import asyncio
import concurrent.futures
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from nano_banana_generator import export_nano_banana_story_set
from story_renderer import export_story_pngs
from story_orchestrator import StoryOrchestrator

APP_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "uploads" / "story_inputs"
VISUAL_MODE_LABELS = {
    "AI-визуалы": "ai",
    "Свои фото": "user_photos",
    "Смешанный режим": "mixed",
}
STAGE_OPTIONS = ["Hook", "Context", "Value", "CTA"]
TYPE_OPTIONS = ["photo", "video"]


def run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(lambda: asyncio.run(coro))
        return future.result()


def init_session_state():
    st.session_state.setdefault("story_plan", None)
    st.session_state.setdefault("saved_upload_paths", [])
    st.session_state.setdefault("upload_registry", {})
    st.session_state.setdefault("render_export", None)
    st.session_state.setdefault("render_mode", None)
    st.session_state.setdefault("realtime_images", [])
    
    if "system_prompt" not in st.session_state:
        try:
            with open(APP_DIR / "GEMINI_STORY_ENGINE.md", "r", encoding="utf-8") as f:
                st.session_state["system_prompt"] = f.read()
        except Exception:
            st.session_state["system_prompt"] = ""


def persist_uploaded_files(uploaded_files):
    if not uploaded_files:
        st.session_state["saved_upload_paths"] = []
        return []

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    registry = st.session_state.setdefault("upload_registry", {})

    for uploaded in uploaded_files:
        file_bytes = uploaded.getvalue()
        file_hash = hashlib.md5(file_bytes).hexdigest()[:12]
        safe_name = f"{file_hash}_{Path(uploaded.name).name.replace(' ', '_')}"
        target_path = UPLOAD_DIR / safe_name

        if not target_path.exists():
            target_path.write_bytes(file_bytes)

        registry[uploaded.name] = str(target_path)
        saved_paths.append(str(target_path))

    st.session_state["saved_upload_paths"] = saved_paths
    return saved_paths


def build_style_prompt(base_style, visual_mode):
    mode_hint = {
        "ai": "Опирайся на AI-визуалы и кинематографичные сцены.",
        "user_photos": "Опирайся на реальные пользовательские фото и делай сценарий удобным для наложения текста.",
        "mixed": "Сочетай реальные фото пользователя и AI-визуалы там, где это усиливает сторителлинг.",
    }[visual_mode]

    base_style = base_style.strip()
    return f"{base_style} {mode_hint}".strip()


def apply_media_defaults(plan, visual_mode, saved_upload_paths):
    stories = plan.get("stories", [])

    for slide in stories:
        slide["generation_mode"] = visual_mode
        if visual_mode == "ai":
            slide.pop("source_image_path", None)

    if not saved_upload_paths or visual_mode == "ai":
        return plan

    assignable_slides = [slide for slide in stories if slide.get("type", "photo") != "video"] or stories

    for index, slide in enumerate(assignable_slides):
        if visual_mode == "user_photos":
            slide["source_image_path"] = saved_upload_paths[index % len(saved_upload_paths)]
        elif visual_mode == "mixed" and index < len(saved_upload_paths):
            slide["source_image_path"] = saved_upload_paths[index]

    return plan


def build_editor_plan(image_options, goal="", audience="", style=""):
    stories = []
    current_plan = st.session_state.get("story_plan") or {"stories": []}

    for idx, slide in enumerate(current_plan.get("stories", [])):
        with st.expander(f"Слайд {slide.get('slide_number', idx + 1)} · {slide.get('stage', 'Stage')}", expanded=idx == 0):
            top_left, top_right = st.columns(2)
            stage = top_left.selectbox(
                "Этап",
                STAGE_OPTIONS,
                index=STAGE_OPTIONS.index(slide.get("stage", "Hook")) if slide.get("stage", "Hook") in STAGE_OPTIONS else 0,
                key=f"stage_{idx}",
            )
            slide_type = top_right.selectbox(
                "Тип слайда",
                TYPE_OPTIONS,
                index=TYPE_OPTIONS.index(slide.get("type", "photo")) if slide.get("type", "photo") in TYPE_OPTIONS else 0,
                key=f"type_{idx}",
            )

            script_text = st.text_area(
                "Текст на экране",
                value=slide.get("script_text", ""),
                key=f"script_text_{idx}",
                height=100,
            )
            visual_prompt = st.text_area(
                "Промпт для визуала",
                value=slide.get("visual_prompt", ""),
                key=f"visual_prompt_{idx}",
                height=120,
            )
            layout_instructions = st.text_area(
                "Инструкции по композиции / тексту",
                value=slide.get("layout_instructions", ""),
                key=f"layout_instructions_{idx}",
                height=80,
            )
            audio_suggestion = st.text_input(
                "Аудио / тон",
                value=slide.get("audio_suggestion", ""),
                key=f"audio_suggestion_{idx}",
            )

            selected_image = slide.get("source_image_path") or "AI / не использовать"
            if selected_image not in image_options:
                selected_image = "AI / не использовать"

            source_image = st.selectbox(
                "Фото для слайда",
                image_options,
                index=image_options.index(selected_image),
                key=f"source_image_{idx}",
            )

            updated_slide = {
                "slide_number": slide.get("slide_number", idx + 1),
                "stage": stage,
                "type": slide_type,
                "script_text": script_text,
                "visual_prompt": visual_prompt,
                "layout_instructions": layout_instructions,
                "audio_suggestion": audio_suggestion,
                "generation_mode": slide.get("generation_mode", "ai"),
            }

            if source_image != "AI / не использовать":
                updated_slide["source_image_path"] = source_image

            # Regenerate Slide Button
            if st.button(f"🎨 Перегенерировать визуал слайда {idx+1}", key=f"regen_btn_{idx}"):
                try:
                    from nano_banana_generator import generate_story_image
                    
                    # Use current values from session state for the prompt
                    temp_slide = updated_slide.copy()
                    
                    with st.spinner(f"Генерирую новый визуал для слайда {idx+1}..."):
                        refresh_dir = APP_DIR / "outputs" / "refreshes"
                        refresh_dir.mkdir(parents=True, exist_ok=True)
                        
                        timestamp = datetime.now().strftime("%H%M%S")
                        file_stub = refresh_dir / f"slide_{idx+1}_{timestamp}"
                        
                        result = generate_story_image(
                            temp_slide, 
                            file_stub, 
                            story_context={
                                "goal": goal,
                                "audience": audience,
                                "style": style,
                            }
                        )
                        
                        st.success(f"Визуал для слайда {idx+1} обновлен!")
                        st.image(result["file_path"], caption=f"Новый вариант слайда {idx+1}", use_container_width=True)
                except Exception as e:
                    st.error(f"Ошибка при регенерации слайда: {e}")

            stories.append(updated_slide)

    return {"stories": stories}


st.set_page_config(page_title="Story Factory", page_icon="🎬", layout="wide")
init_session_state()

st.title("🎬 Story Factory — Stories по методу Тимочко")
st.caption(
    "Gemini генерирует структуру Hook → Context → Value → CTA, а Google Vids / fallback-пайплайн обрабатывают визуалы."
)

st.info(
    "Важно: кнопка **«Сгенерировать план сторис»** делает только сценарий. "
    "Чтобы получить реальные AI-картинки, ниже нажми **«🍌 Создать AI сторис (Nano Banana Pro)»**. "
    "Локальный PNG-рендер оставлен как fallback. Если хочешь прогон через Google Vids/автоматизацию, используй отдельную кнопку внешнего пайплайна."
)

with st.sidebar:
    st.header("Статус")
    if os.environ.get("GOOGLE_API_KEY"):
        st.success("GOOGLE_API_KEY найден")
    else:
        st.warning("GOOGLE_API_KEY не найден. Проверь .env")

    if (APP_DIR / "google_auth.json").exists():
        st.success("google_auth.json найден")
    else:
        st.info("Для Google Vids сначала запусти python google_content_factory/save_auth.py")

    st.markdown("**Запуск приложения**")
    st.code("python3 -m streamlit run app.py")

with st.form("story_generation_form"):
    goal = st.text_area(
        "Что нужно продать / донести? (Цель конкретной серии сторис)",
        value="Продать курс по ИИ-автоматизации для новичков",
        height=100,
    )
    strategy = st.text_area(
        "Зачем тебе вести блог? (Глобальная стратегия / Твоя миссия)",
        value="Помогаю экспертам внедрять ИИ, чтобы они работали меньше, а зарабатывали больше. Строю личный бренд как топ-эксперта в автоматизации.",
        height=100,
    )
    audience = st.text_input(
        "Целевая аудитория",
        value="Владельцы малого бизнеса и фрилансеры",
    )
    style = st.text_input(
        "Стиль",
        value="Современный, профессиональный, технологичный, но доступный",
    )

    storyline_type = st.radio(
        "Тип сюжетной линии (по Тимочко)",
        options=["Expert", "Personal", "Lifestyle"],
        index=0,
        horizontal=True,
        help="Expert: авторитет и кейсы. Personal: уязвимость и ценности. Lifestyle: эстетика и 'мечта'.",
    )
    
    with st.expander("⚙️ Настройка системного промпта (Engine Rules)"):
        custom_system_prompt = st.text_area(
            "System Instruction",
            value=st.session_state["system_prompt"],
            height=300,
        )
        st.session_state["system_prompt"] = custom_system_prompt

    visual_mode_label = st.radio(
        "Режим визуалов",
        options=list(VISUAL_MODE_LABELS.keys()),
        horizontal=True,
        help="Свои фото — упор на загруженные изображения. Смешанный — часть слайдов на фото, часть на AI.",
    )
    uploaded_files = st.file_uploader(
        "Загрузи свои фото (необязательно)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )
    generate_plan = st.form_submit_button("Сгенерировать план сторис")

if generate_plan:
    try:
        visual_mode = VISUAL_MODE_LABELS[visual_mode_label]
        saved_upload_paths = persist_uploaded_files(uploaded_files)
        orchestrator = StoryOrchestrator()

        with st.spinner("Gemini генерирует сценарий..."):
            plan = run_async(
                orchestrator.generate_story_plan(
                    goal,
                    audience,
                    build_style_prompt(style, visual_mode),
                    storyline_type=storyline_type,
                    strategy=strategy,
                    custom_system_prompt=st.session_state["system_prompt"]
                )
            )

        if not plan:
            st.error("Gemini вернул пустой или некорректный план.")
        else:
            st.session_state["story_plan"] = apply_media_defaults(plan, visual_mode, saved_upload_paths)
            st.session_state["story_goal"] = goal
            st.session_state["story_strategy"] = strategy
            st.session_state["story_audience"] = audience
            st.session_state["story_style"] = style
            st.session_state["render_export"] = None
            st.session_state["realtime_images"] = []
            st.success(f"План сторис готов. Использована модель: {orchestrator.model_name}")
    except Exception as error:
        st.error(f"Не удалось сгенерировать план: {error}")

if uploaded_files:
    st.subheader("Загруженные фото")
    preview_columns = st.columns(min(4, len(uploaded_files)))
    for index, uploaded in enumerate(uploaded_files):
        preview_columns[index % len(preview_columns)].image(uploaded, caption=uploaded.name, use_container_width=True)

if st.session_state.get("story_plan"):
    plan = st.session_state["story_plan"]
    stories = plan.get("stories", [])
    video_count = sum(1 for slide in stories if slide.get("type") == "video")
    photo_count = len(stories) - video_count

    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Слайдов", len(stories))
    metric_b.metric("Видео", video_count)
    metric_c.metric("Фото / статичных", photo_count)

    # Rework Plan Section
    with st.expander("🔄 Доработать план (Feedback loop)", expanded=False):
        st.markdown("Если сценарий не идеален, напиши что исправить, и Gemini переделает весь план целиком.")
        rework_feedback = st.text_area("Твой фидбек", placeholder="Например: сделай более дерзко, добавь больше юмора или измени CTA на подписку", key="rework_feedback_input")
        if st.button("🚀 Переделать план", use_container_width=True):
            if rework_feedback:
                try:
                    orchestrator = StoryOrchestrator()
                    with st.spinner("Gemini переделывает план с учетом фидбека..."):
                        new_plan = run_async(orchestrator.rework_story_plan(
                            st.session_state["story_plan"],
                            rework_feedback,
                            custom_system_prompt=st.session_state["system_prompt"]
                        ))
                    if new_plan:
                        st.session_state["story_plan"] = new_plan
                        st.success("План успешно обновлен!")
                        st.rerun()
                    else:
                        st.error("Не удалось получить обновленный план.")
                except Exception as e:
                    st.error(f"Ошибка при доработке: {e}")
            else:
                st.warning("Пожалуйста, введите текст фидбека.")

    st.subheader("Редактор сценария")
    image_options = ["AI / не использовать", *st.session_state.get("saved_upload_paths", [])]

    with st.expander("🔎 По какому промпту сейчас генерируется текст и ТЗ сторис"):
        meta = plan.get("_meta", {})
        if meta:
            st.markdown("**Системный промпт (правила движка сторис):**")
            st.code(meta.get("story_engine_system_prompt", ""), language="markdown")
            st.markdown("**Пользовательский prompt, который подставляется в Gemini:**")
            st.code(meta.get("story_engine_user_prompt", ""), language="text")
            st.markdown("**Полный prompt (system + user), который идёт в Gemini:**")
            st.code(meta.get("story_engine_full_prompt", ""), language="text")
        else:
            st.info("Meta-информация по prompt пока не найдена в плане.")

    # Editor Section
    edited_plan = build_editor_plan(
        image_options, 
        goal=st.session_state.get("story_goal", ""), 
        audience=st.session_state.get("story_audience", ""), 
        style=st.session_state.get("story_style", "")
    )
    
    if st.button("💾 Сохранить все текстовые правки", use_container_width=True):
        st.session_state["story_plan"] = edited_plan
        st.success("Правки сохранены.")

    action_left, action_mid_left, action_mid_right, action_right, action_fifth = st.columns(5)

    with action_left:
        if st.button("🍌 Создать AI сторис (Nano Banana Pro)", use_container_width=True):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                image_grid_placeholder = st.empty()
                st.session_state["realtime_images"] = []

                def update_progress(current, total, stage):
                    percent = int((current / total) * 100)
                    progress_bar.progress(percent)
                    status_text.text(f"Генерация слайда {current} из {total} ({stage})...")
                    
                    # Update image grid in real-time
                    # We need to find the latest generated file. 
                    # Since export_nano_banana_story_set doesn't return partial results easily,
                    # we'll rely on the fact that it saves files to a predictable directory.
                    # However, a better way is to modify export_nano_banana_story_set to pass back the new file path.
                    # For now, let's just show the progress and we'll handle the grid update after each slide.
                    pass

                # To support real-time display, we'll modify the callback to also receive the file path
                def progress_with_image(current, total, stage, file_path=None):
                    percent = int((current / total) * 100)
                    progress_bar.progress(percent)
                    status_text.text(f"Генерация слайда {current} из {total} ({stage})...")
                    if file_path:
                        st.session_state["realtime_images"].append(file_path)
                        with image_grid_placeholder.container():
                            cols = st.columns(3)
                            for i, img_path in enumerate(st.session_state["realtime_images"]):
                                cols[i % 3].image(img_path, caption=f"Слайд {i+1}", use_container_width=True)

                with st.spinner("Генерирую реальные AI-сторис через Nano Banana Pro..."):
                    # We need to update export_nano_banana_story_set to support this new callback signature
                    export_result = export_nano_banana_story_set(
                        st.session_state["story_plan"],
                        project_name=goal,
                        story_context={
                            "goal": goal,
                            "strategy": st.session_state.get("story_strategy", ""),
                            "audience": audience,
                            "style": style,
                        },
                        progress_callback=progress_with_image,
                    )
                st.session_state["render_export"] = export_result
                progress_bar.empty()
                status_text.empty()
                st.session_state["render_mode"] = "nano_banana_pro"
                st.success(f"AI-сторис готовы через {export_result['model']}: {export_result['output_dir']}")
            except Exception as error:
                st.error(f"Не удалось создать AI-сторис через Nano Banana Pro: {error}")

    with action_mid_left:
        if st.button("🧩 Локальный fallback PNG", use_container_width=True):
            try:
                with st.spinner("Собираю готовые статичные сторис в PNG..."):
                    export_result = export_story_pngs(
                        st.session_state["story_plan"],
                        project_name=goal,
                    )
                st.session_state["render_export"] = export_result
                st.session_state["render_mode"] = "local_png"
                st.success(f"PNG-сторис готовы: {export_result['output_dir']}")
            except Exception as error:
                st.error(f"Не удалось создать PNG сторис: {error}")

    with action_mid_right:
        if st.button("🎞️ Внешний пайплайн / Google Vids", use_container_width=True):
            try:
                orchestrator = StoryOrchestrator()
                with st.spinner("Запускаю внешний пайплайн по слайдам..."):
                    run_async(orchestrator.process_story_plan(st.session_state["story_plan"]))
                st.success("Внешний пайплайн завершен. Проверь терминал и итоговые файлы.")
            except Exception as error:
                st.error(f"Ошибка во время обработки: {error}")

    with action_right:
        st.download_button(
            "⬇️ Скачать JSON",
            data=json.dumps(st.session_state["story_plan"], ensure_ascii=False, indent=2),
            file_name="story_plan.json",
            mime="application/json",
            use_container_width=True,
        )

    with action_fifth:
        if st.button("🧹 Очистить план", use_container_width=True):
            st.session_state["story_plan"] = None
            st.session_state["render_export"] = None
            st.session_state["render_mode"] = None
            st.rerun()

    if st.session_state.get("render_export"):
        render_export = st.session_state["render_export"]
        render_mode = st.session_state.get("render_mode") or render_export.get("generator") or "local_png"

        if render_mode == "nano_banana_pro":
            st.subheader("Готовые AI сторис — Nano Banana Pro")
            st.success(
                f"Это уже не PIL-макет, а AI-рендер через {render_export.get('model', 'Nano Banana Pro')}. "
                f"Папка: {render_export['output_dir']}"
            )
        else:
            st.subheader("Готовые PNG сторис")
            st.success(
                "Это локальный fallback-рендер. Теперь у тебя не только план, а уже реальные сторис-картинки 1080×1920. "
                f"Папка: {render_export['output_dir']}"
            )

        with open(render_export["zip_path"], "rb") as archive_file:
            st.download_button(
                "⬇️ Скачать все PNG одним ZIP",
                data=archive_file.read(),
                file_name=Path(render_export["zip_path"]).name,
                mime="application/zip",
                use_container_width=True,
            )

        preview_files = render_export.get("files", [])

        if preview_files:
            st.subheader("Результат прямо на сайте")
            selected_index = st.selectbox(
                "Выбери сторис для крупного просмотра",
                options=list(range(len(preview_files))),
                format_func=lambda index: f"Слайд {index + 1} · {Path(preview_files[index]).stem}",
                key="selected_render_preview_index",
            )

            preview_left, preview_center, preview_right = st.columns([1, 2, 1])
            with preview_center:
                st.image(
                    preview_files[selected_index],
                    caption=f"Крупный просмотр: {Path(preview_files[selected_index]).name}",
                    use_container_width=True,
                )

            st.caption(
                "Ниже показана вся серия сторис. То есть результат можно смотреть прямо на сайте, "
                "не только скачивать ZIP."
            )

            if render_export.get("prompts"):
                with st.expander("🧠 Промпты Nano Banana Pro по каждому слайду"):
                    for prompt_item in render_export["prompts"]:
                        st.markdown(
                            f"**Слайд {prompt_item['slide_number']} · {prompt_item['stage']}**  \\n+Текст: `{prompt_item['script_text']}`"
                        )
                        st.code(prompt_item["prompt"], language="text")

            gallery_columns = st.columns(min(3, len(preview_files)) or 1)
            for index, preview_file in enumerate(preview_files):
                gallery_columns[index % len(gallery_columns)].image(
                    preview_file,
                    caption=f"Слайд {index + 1}",
                    use_container_width=True,
                )

    st.subheader("JSON-предпросмотр")
    st.json(st.session_state["story_plan"])
else:
    st.info("Сгенерируй план сторис, чтобы открыть редактор и запуск обработки.")