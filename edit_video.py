import requests
import subprocess
import json
import feedparser
import time
import os
from sql import init_db, save_video_id, get_all_video_ids, update_video_status

RAPIDAPI_HOST = "youtube-mp4-mp3-downloader.p.rapidapi.com"
RAPIDAPI_KEY = "3a1024cc78msh53c77f4992c0ed9p1b62f6jsnc027eb0021d0"

headers = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY
}


def concat_videos_ffmpeg(video1, video2, output_video):
    # Временные перекодированные файлы
    tmp1 = "tmp1.mp4"
    tmp2 = "tmp2.mp4"

    # Шаг 1: перекодируем первое видео (обрезаем до 10 секунд)
    subprocess.run([
        "ffmpeg", "-i", video1,
        "-vf", "scale=1080:1920,setsar=1",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        "-y", tmp1
    ], check=True)

    # Шаг 2: перекодируем второе видео без обрезки
    subprocess.run([
        "ffmpeg", "-i", video2,
        "-vf", "scale=1080:1920,setsar=1",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        "-y", tmp2
    ], check=True)

    # Шаг 3: создаём текстовый файл со списком для конкатенации
    with open("list.txt", "w") as f:
        f.write(f"file '{tmp1}'\n")
        f.write(f"file '{tmp2}'\n")

    # Шаг 4: конкатенация без повторного перекодирования
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", "list.txt", "-c", "copy", "-y", output_video
    ], check=True)

    print(f"Склеенные видео сохранены в {output_video}")


def get_video_duration(video_path: str) -> float:
    """Возвращает длительность видео в секундах."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"⚠️ Не удалось получить длительность видео: {result.stderr}")
    return float(result.stdout.strip())


def concat_videos(video1, video2, output_video):
    """Склеивает два видео в одно."""
    list_file = "videos_to_concat.txt"
    with open(list_file, "w") as f:
        f.write(f"file '{os.path.abspath(video1)}'\n")
        f.write(f"file '{os.path.abspath(video2)}'\n")

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        "-y",
        output_video
    ]
    subprocess.run(cmd, check=True)
    print(f"🎞️ Видео {video1} и {video2} склеены в {output_video}")


def main():
    duration = get_video_duration("main.mp4")
    print(f"⏱️ Длительность первого видео: {duration:.2f} сек")

    if duration >= 60:
        print("✅ Видео длиннее 1 минуты — сохраняем как res.mp4 без изменений.")
        os.rename("main.mp4", "res.mp4")
    elif duration >= 45 and duration < 60:
        print("⚠️ Видео длится от 45 до 60 секунд — обрабатываем как короткое.")
        concat_videos_ffmpeg("main.mp4", "15.mp4", "res.mp4")
        
    else:
        print("⚠️ Видео короче 1 минуты — скачиваем ещё одно для склейки.")    
        concat_videos("main.mp4", "main.mp4", "res.mp4")

    print("🏁 Готово: файл res.mp4 создан.")


if __name__ == "__main__":
    main()
