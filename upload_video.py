import requests
import subprocess
import json
import feedparser
from sql import init_db, save_video_id, get_all_video_ids, update_video_status


API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im5pa2l0YWQ1ODkwQGdtYWlsLmNvbSIsImV4cCI6NDkxMTc4ODU2MywianRpIjoiOTc2MjM1ZjctZDEwMy00NDgxLWI2NzItODQ4OWFkODgyYzlhIn0.FgyGGk3ymOnA_4GwKTwVFvA2dc0h2NFm0TCcxbE9ntw"

def upload(social, video_path, title):
    url = "https://api.upload-post.com/api/upload"
    headers = {
        "Authorization": f"Apikey {API_KEY}"
    }
    data = {
        "title": title,
        "user": "baobao",
        "platform[]": {social}  # 👈 ключевое — загружаем на Instagram
    }
    files = {
        "video": open(video_path, "rb")
    }

    response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        print("✅ Видео успешно отправлено")
        print(response.json())
        return response.json()
    else:
        print(f"❌ Ошибка загрузки ({response.status_code}): {response.text}")
        return None


if __name__ == "__main__":
    upload(social ="tiktok", video_path="res.mp4", title="Изучайте китайский на https://baobao.by")
    upload(social="youtube", video_path="res.mp4", title="Изучайте китайский на https://baobao.by")
    upload(social="instagram", video_path="res.mp4", title="Изучайте китайский на https://baobao.by")