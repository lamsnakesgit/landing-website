import cv2
import json
import os
import sys

def analyze_video_layout(video_path):
    print(f"[*] Запуск Анализатора Композиции для: {video_path}")
    
    if not os.path.exists(video_path):
        print(f"Ошибка: Файл {video_path} не найден.")
        sys.exit(1)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Ошибка: Не удалось открыть {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Используем встроенный каскад OpenCV
    face_cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    # Проверяем кадры каждую секунду
    interval = int(fps) 
    
    layout_timeline = []
    
    for f in range(0, total_frames, interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Оптимизация: ищем лица
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        current_time = round(f / fps, 2)
        layout = "B_ROLL"
        
        if len(faces) > 0:
            # Берем самое большое лицо
            faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
            x, y, w, h = faces[0]
            
            face_center_y = y + h // 2
            face_area = w * h
            frame_area = width * height
            
            if face_area > frame_area * 0.15:
                layout = "FULL_SCREEN"
            elif face_center_y < height // 2:
                layout = "TOP"
            else:
                layout = "BOTTOM"
        
        # Убираем дубликаты состояний, чтобы формировать сцены
        if len(layout_timeline) > 0 and layout_timeline[-1]['layout'] == layout:
            layout_timeline[-1]['end_time'] = round(current_time + 1.0, 2)
        else:
            layout_timeline.append({
                "layout": layout,
                "start_time": current_time,
                "end_time": round(current_time + 1.0, 2)
            })

    cap.release()
    
    output_data = {
        "video": video_path,
        "resolution": f"{width}x{height}",
        "timeline": layout_timeline
    }
    
    with open("layout_analysis.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)
        
    print("[+] Анализ завершен! Сохранено в layout_analysis.json")
    for scene in layout_timeline:
        print(f"  [{scene['start_time']}s - {scene['end_time']}s] -> {scene['layout']}")
        
    return output_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 layout_analyzer.py <путь_к_видео>")
        sys.exit(1)
    analyze_video_layout(sys.argv[1])
