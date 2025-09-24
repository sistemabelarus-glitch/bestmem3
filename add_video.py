import feedparser
from sql import init_db, save_video_id


def get_latest_shorts():
    max_results = 15
    channel_ids = ["UCw7SXwdelegoyM6hrM-qAwQ"]
    shorts_ids = []

    for channel_id in channel_ids:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"⚠️ Не удалось получить видео с канала {channel_id}")
            continue

        # фильтруем только shorts
        for entry in feed.entries[:max_results]:
            if "shorts/" in entry.link:  # проверка на формат Shorts
                shorts_ids.append(entry.yt_videoid)

    init_db()  # создаём базу, если её ещё нет
    for vid in shorts_ids:
        save_video_id(vid)

if __name__ == "__main__":
    get_latest_shorts()
