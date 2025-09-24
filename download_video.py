import requests
import subprocess
import json
import feedparser
from sql import init_db, save_video_id, get_all_video_ids, update_video_status

def download_youtube_video(video_id, output_file):
    api_url = f"https://youtube-video-fast-downloader-24-7.p.rapidapi.com/download_short/{video_id}"
    headers = {
        "x-rapidapi-host": "youtube-video-fast-downloader-24-7.p.rapidapi.com",
        "x-rapidapi-key": "67986ba9cemshbb17d65db207fc3p110386jsne22a822448d8"
    }

    params = {
        "quality": 247
    }

    # Получаем JSON с ссылкой на видео
    response = requests.get(api_url, headers=headers, params=params )
    if response.status_code != 200:
        raise Exception(f"Ошибка API: {response.status_code}, {response.text}")

    data = response.json()
    print(json.dumps(data, indent=4, ensure_ascii=False))

    # Предположим, что JSON содержит ключ 'download_url'
    video_url = data.get("file")
    if not video_url:
        raise Exception(f"Ссылка на видео не найдена в JSON: {data}")

    # Скачиваем видео по полученной ссылке
    print(f"Скачиваем видео {video_id} по ссылке {video_url}...")
    video_resp = requests.get(video_url, stream=True)
    if video_resp.status_code == 200:
        with open(output_file, "wb") as f:
            for chunk in video_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Видео {video_id} сохранено как {output_file}")

        update_video_status(video_id, "downloaded", "videos.db")

    else:
        raise Exception(f"Ошибка при скачивании видео: {video_resp.status_code}")

if __name__ == "__main__":
    new_videos = [v for v in get_all_video_ids() if v["status"] == "new"]

    main_video_id = new_videos[0]['video_id']
    download_youtube_video(main_video_id, "main.mp4")