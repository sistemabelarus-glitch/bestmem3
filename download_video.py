import requests
import time

RAPIDAPI_HOST = "youtube-mp4-mp3-downloader.p.rapidapi.com"
RAPIDAPI_KEY = "3a1024cc78msh53c77f4992c0ed9p1b62f6jsnc027eb0021d0"

headers = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY
}

def download_youtube_video(video_id: str, output_file: str):
    """Скачивает YouTube-видео через RapidAPI по его ID"""

    # 1. Старт задачи
    download_url = f"https://{RAPIDAPI_HOST}/api/v1/download"
    params = {
        "format": "720",
        "id": video_id,
        "audioQuality": "128",
        "addInfo": "false"
    }

    print(f"Запускаем задачу для {video_id}...")
    resp_download = requests.get(download_url, headers=headers, params=params)
    resp_json = resp_download.json()
    print("Ответ download:", resp_json)

    progress_id = resp_json.get("progressId")
    if not progress_id:
        raise ValueError("❌ Не удалось получить progressId")

    # 2. Ждём 20 секунд (или можно опрашивать циклом)
    print("⏳ Ждём 20 секунд...")
    time.sleep(20)

    # 3. Проверка прогресса
    progress_url = f"https://{RAPIDAPI_HOST}/api/v1/progress"
    params_progress = {"id": progress_id}

    print("Проверяем прогресс...")
    resp_progress = requests.get(progress_url, headers=headers, params=params_progress)
    progress_json = resp_progress.json()
    print("Ответ progress:", progress_json)

    download_link = progress_json.get("downloadUrl")
    if not download_link:
        raise ValueError("❌ Не удалось найти downloadUrl в ответе API")

    # 4. Скачивание файла
    print(f"⬇️ Скачиваем: {download_link}")
    with requests.get(download_link, stream=True) as r:
        r.raise_for_status()
        with open(output_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print(f"✅ Видео сохранено как {output_file}")

if __name__ == "__main__":
    new_videos = [v for v in get_all_video_ids() if v["status"] == "new"]

    main_video_id = new_videos[0]['video_id']
    download_youtube_video(main_video_id, "main.mp4")
