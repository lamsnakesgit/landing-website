import json
import os
import subprocess
import sys

def assemble_video(original_video, layout_json, avatar_clips_dir, output_path):
    print(f"[*] Запуск Умной Сборки: {output_path}")
    
    with open(layout_json, 'r') as f:
        data = json.load(f)
        
    timeline = data['timeline']
    
    # Сначала соберем все аватар-клипы в один длинный трек
    # (Допустим, они названы clip_0.mp4, clip_1.mp4...)
    # Для этого примера предполагаем, что у нас есть единый аватар-видео, либо мы склеиваем их.
    # В реальной задаче: собираем сгенерированные Veo клипы в один длинный avatar.mp4
    
    # Для теста: просто берем сгенерированный veo_test.mp4
    sample_clip = "veo_test.mp4"
    if not os.path.exists(sample_clip):
        print(f"[-] Нет клипов: {sample_clip}")
        return False
        
    # Формируем сложный фильтр FFmpeg на основе timeline
    # Нам нужно наложить sample_clip на original_video, 
    # меняя его позицию в зависимости от времени.
    
    filter_complex = f"[0:v]scale=1080:1920[bg]; [1:v]scale=500:500[avatar]; "
    overlay_expr = ""
    
    # Строим выражение для overlay (x и y) с помощью функций between(t, start, end)
    x_exprs = []
    y_exprs = []
    enable_exprs = []
    
    for scene in timeline:
        start = scene['start_time']
        end = scene['end_time']
        layout = scene['layout']
        
        cond = f"between(t,{start},{end})"
        
        if layout == "B_ROLL":
            # Не показываем аватара
            pass
        else:
            enable_exprs.append(cond)
            if layout == "BOTTOM":
                x_exprs.append(f"if({cond}, (W-w)/2, 0)")
                y_exprs.append(f"if({cond}, H-h-100, 0)")
            elif layout == "TOP":
                x_exprs.append(f"if({cond}, (W-w)/2, 0)")
                y_exprs.append(f"if({cond}, 100, 0)")
            elif layout == "FULL_SCREEN":
                x_exprs.append(f"if({cond}, (W-w)/2, 0)")
                y_exprs.append(f"if({cond}, (H-h)/2, 0)")
                
    if not enable_exprs:
        print("[-] На карте только B_ROLL, аватар не нужен.")
        return False
        
    enable_str = "+".join(enable_exprs)
    
    # Собираем вложенные if-else для X и Y
    # Поскольку FFmpeg выражения сложные, сделаем проще: используем enable 
    # для управления показом аватара, а позицию сделаем динамической.
    
    # Формируем цепочку overlay. Если позиция меняется, проще разрезать аватар 
    # на куски и накладывать каждый кусок отдельно, но мы используем динамический X/Y:
    x_final = x_exprs[0]
    y_final = y_exprs[0]
    for i in range(1, len(x_exprs)):
        x_final = x_final.replace(", 0)", f", {x_exprs[i]})")
        y_final = y_final.replace(", 0)", f", {y_exprs[i]})")
        
    filter_complex += f"[bg][avatar]overlay=x='{x_final}':y='{y_final}':enable='{enable_str}'[outv]"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", original_video,
        "-stream_loop", "-1", "-i", sample_clip, # Зацикливаем аватар для теста
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a", # Берем оригинальный звук (или звук из Veo, если нужно)
        "-shortest",
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]
    
    print("[*] Рендеринг финального видео...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[+] Сборка завершена: {output_path}")
    return True

if __name__ == "__main__":
    if not os.path.exists("veo_clips"):
        os.makedirs("veo_clips")
        # Создадим заглушку
        os.system("ffmpeg -f lavfi -i color=c=blue:s=500x500:d=5 -c:v libx264 -y veo_clips/clip_0.mp4 > /dev/null 2>&1")
        
    assemble_video(
        "../04_Design_and_Media/spy_downloads/kaisar_reel.mp4", 
        "layout_analysis.json", 
        "veo_clips", 
        "final_smart_video.mp4"
    )
