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


def download_youtube_video(video_id: str, output_file: str, poll_interval: int = 5, timeout: int = 300):
    """Скачивает YouTube-видео через RapidAPI и сохраняет в файл."""
    download_url = f"https://{RAPIDAPI_HOST}/api/v1/download"
    params = {
        "format": "720",
        "id": video_id,
        "audioQuality": "128",
        "addInfo": "false"
    }

    print(f"🎬 Запускаем задачу для {video_id}...")
    resp_download = requests.get(download_url, headers=headers, params=params)
    resp_json = resp_download.json()
    print("Ответ download:", resp_json)

    progress_id = resp_json.get("progressId")
    if not progress_id:
        raise ValueError("❌ Не удалось получить progressId")

    # Опрос прогресса
    progress_url = f"https://{RAPIDAPI_HOST}/api/v1/progress"
    params_progress = {"id": progress_id}
    elapsed = 0
    download_link = None

    print("⏳ Ожидаем готовности файла...")
    while elapsed < timeout:
        resp_progress = requests.get(progress_url, headers=headers, params=params_progress)
        progress_json = resp_progress.json()
        print("Ответ progress:", progress_json)

        if progress_json.get("finished"):
            download_link = progress_json.get("downloadUrl")
            if download_link:
                break
        time.sleep(poll_interval)
        elapsed += poll_interval

    if not download_link:
        raise TimeoutError(f"❌ Видео не готово за {timeout} секунд")

    # Скачивание файла
    print(f"⬇️ Скачиваем: {download_link}")
    with requests.get(download_link, stream=True) as r:
        r.raise_for_status()
        with open(output_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    print(f"✅ Видео сохранено как {output_file}")


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
    init_db()

    # 🔹 Получаем список ID из базы
    video_ids = get_all_video_ids()
    if not video_ids:
        print("⚠️ Нет видео ID в базе.")
        return

    first_video_id = video_ids[0]
    download_youtube_video(first_video_id, "main.mp4")
    duration = get_video_duration("main.mp4")
    print(f"⏱️ Длительность первого видео: {duration:.2f} сек")

    if duration >= 60:
        print("✅ Видео длиннее 1 минуты — сохраняем как res.mp4 без изменений.")
        os.rename("main.mp4", "res.mp4")
    else:
        print("⚠️ Видео короче 1 минуты — скачиваем ещё одно для склейки.")
        if len(video_ids) < 2:
            print("❌ Нет второго видео для склейки.")
            os.rename("main.mp4", "res.mp4")
            return

        second_video_id = video_ids[1]
        download_youtube_video(second_video_id, "second.mp4")
        concat_videos("main.mp4", "second.mp4", "res.mp4")

    print("🏁 Готово: файл res.mp4 создан.")


if __name__ == "__main__":
    main()
