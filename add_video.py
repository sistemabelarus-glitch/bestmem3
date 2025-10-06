import feedparser
from sql import init_db, save_video_id

def get_latest_shorts():
    max_results = 15
    channel_ids = [
        "UCVRm2Ho8cL3lvWDyp2ayuFw",
        "UCmaPCGY_yGcHDEleS9s3W_w",
        "UCESLZhusAkFfsNsApnjF_Cg",
        "UCjjBjVc0b1cIpNGEeZtS2lg"
    ]
    shorts = []

    for channel_id in channel_ids:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"⚠️ Не удалось получить видео с канала {channel_id}")
            continue

        for entry in feed.entries[:max_results]:
            if "shorts/" in entry.link:  # проверка на Shorts
                shorts.append((entry.yt_videoid, entry.title))

    init_db()  # создаём базу, если её ещё нет
    for vid, title in shorts:
        save_video_id(vid, title)


if __name__ == "__main__":
    get_latest_shorts()
