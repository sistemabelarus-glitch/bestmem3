import requests
import time
from sql import init_db, save_video_id, get_all_video_ids, update_video_status

RAPIDAPI_HOST = "youtube-mp4-mp3-downloader.p.rapidapi.com"
RAPIDAPI_KEY = "3a1024cc78msh53c77f4992c0ed9p1b62f6jsnc027eb0021d0"

headers = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY
}

def download_youtube_video(video_id: str, output_file: str, poll_interval: int = 5, timeout: int = 300):
    """
    Скачивает YouTube-видео через RapidAPI.
    - video_id: ID ролика YouTube
    - output_file: имя выходного файла
    - poll_interval: пауза между проверками прогресса (сек)
    - timeout: максимальное время ожидания (сек)
    """

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

    # 2. Опрос прогресса
    progress_url = f"https://{RAPIDAPI_HOST}/api/v1/progress"
    params_progress = {"id": progress_id}

    download_link = None
    elapsed = 0

    print("Ожидаем готовности файла...")
    while elapsed < timeout:
        resp_progress = requests.get(progress_url, headers=headers, params=params_progress)
        progress_json = resp_progress.json()
        print("Ответ progress:", progress_json)

        download_link = progress_json.get("downloadUrl")
        if progress_json.get("finished") and download_link:
            break

        time.sleep(poll_interval)
        elapsed += poll_interval

    if not download_link:
        raise TimeoutError(f"❌ Видео не готово за {timeout} секунд")

    # 3. Скачивание файла
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
