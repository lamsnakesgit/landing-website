import os
import shutil
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json

class SmartEditor:
    """
    Модуль для создания графических оверлеев и управления умным монтажом.
    """
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.overlay_dir = self.base_dir / "outputs" / "overlays"
        self.overlay_dir.mkdir(parents=True, exist_ok=True)
        # На Mac используем Helvetica или Arial
        self.font_path = "/System/Library/Fonts/Helvetica.ttc" 
        if not Path(self.font_path).exists():
            self.font_path = "/Library/Fonts/Arial Unicode.ttf"

    def create_text_overlay(self, text, filename, width=720, height=1280, font_size=55):
        """
        Создает прозрачный PNG с текстом в стиле Hormozi (ALL CAPS, подложки).
        """
        text = text.upper() # Конвертируем в капс для стиля
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except:
            font = ImageFont.load_default()

        # Настройка стиля "Стикер"
        bg_color = (0, 0, 0, 220) # Более плотная черная подложка
        text_color = (255, 255, 255, 255) # Белый текст
        
        # Умная разбивка текста по пиксельной ширине
        max_pixel_width = width - 120 # Оставляем по 60px отступов по бокам
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            # Измеряем ширину строки в пикселях
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_w = bbox[2] - bbox[0]
            
            if line_w <= max_pixel_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        # Вычисление позиции (150px от низа - максимально низко, но безопасно)
        line_height = font_size + 15
        total_height = len(lines) * line_height
        start_y = height - total_height - 150 
        
        padding = 15
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            x = (width - w) // 2
            y = start_y + i * line_height
            
            # Рисуем закругленную плашку
            draw.rounded_rectangle(
                [x - padding, y - 5, x + w + padding, y + font_size + 10],
                radius=10,
                fill=bg_color
            )
            
            # Рисуем текст
            draw.text((x, y), line, font=font, fill=text_color)

        output_path = self.overlay_dir / filename
        img.save(output_path)
        return output_path

    def create_nick_plate(self, text="t.me/nnsvt", width=720, height=1280):
        """
        Создает плашку с ником в ПРАВОМ НИЖНЕМ углу.
        """
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        font_size = 35
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except:
            font = ImageFont.load_default()

        # Текст ника
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        
        # Позиция: Справа внизу
        margin = 40
        x = width - w - margin - 20 # Запас для паддинга
        y = height - margin - 50
        
        # Рисуем стильную плашку для ника
        draw.rounded_rectangle(
            [x - 15, y - 10, width - margin + 10, y + font_size + 10],
            radius=8,
            fill=(0, 0, 0, 255) # Непрозрачный черный для акцента
        )
        
        # Рисуем текст ника
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        output_path = self.overlay_dir / "nick_plate.png"
        img.save(output_path)
        return output_path
    def create_karaoke_sequence(self, clip_name, words, width=720, height=1280):
        """
        Генерирует серию PNG для караоке-эффекта.
        Каждое слово - отдельный файл с подсветкой.
        """
        clip_overlay_dir = self.overlay_dir / "karaoke" / clip_name.replace(".mp4", "")
        if clip_overlay_dir.exists():
            shutil.rmtree(clip_overlay_dir)
        clip_overlay_dir.mkdir(parents=True, exist_ok=True)
        
        font_size = 75 # Делаем крупнее для акцента на 1 слово
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except:
            font = ImageFont.load_default()
            
        generated_files = []
        
        for i, word_data in enumerate(words):
            text = word_data["word"].upper()
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Позиция (Центр-Низ-Средне, чтобы не на лице и не в кнопках)
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            x = (width - w) // 2
            y = height - 450 # Чуть выше ника, но ниже лица
            
            # Стиль: Черная подложка + Желтый текст
            draw.rounded_rectangle(
                [x - 15, y - 5, x + w + 15, y + font_size + 10],
                radius=10,
                fill=(0, 0, 0, 230)
            )
            
            draw.text((x, y), text, font=font, fill=(255, 204, 0, 255)) # Желтый акцент
            
            filename = f"word_{i:03d}.png"
            path = clip_overlay_dir / filename
            img.save(path)
            generated_files.append({
                "path": path,
                "start": word_data["start"],
                "end": word_data["end"]
            })
            
        return generated_files


if __name__ == "__main__":
    # Тест
    editor = SmartEditor(os.getcwd())
    editor.create_text_overlay("Вчера уволили 20% программистов... \n И дело не в кризисе.", "test_caption.png")
    editor.create_watermark()
    print("✅ Тестовые оверлеи созданы в outputs/overlays/")
