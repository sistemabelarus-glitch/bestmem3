import requests
import subprocess
import json
import feedparser
from sql import init_db, save_video_id, get_all_video_ids, update_video_status

def duplicate_video_ffmpeg(video, output_video):
    # Создаем временный файл со списком (один и тот же файл дважды)
    list_file = "videos_to_concat.txt"
    with open(list_file, "w") as f:
        f.write(f"file '{video}'\n")
        f.write(f"file '{video}'\n")

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",  # без перекодирования
        "-y",
        output_video
    ]

    subprocess.run(cmd, check=True)

    print(f"Видео {video} продублировано и сохранено в {output_video}")

if __name__ == "__main__":
    duplicate_video_ffmpeg("main.mp4", "res.mp4")
