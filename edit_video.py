import requests
import subprocess
import json
import feedparser
from sql import init_db, save_video_id, get_all_video_ids, update_video_status

def overlay_videos_ffmpeg(main_video, square_video, output_video):
    # Получаем размеры основного видео
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "{main_video}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    width, height = map(int, result.stdout.strip().split(','))

    # Размер квадратного видео (1/3 от ширины основного)
    square_size = int(width / 1.5)

    # Позиция квадратного видео (по центру внизу)
    x_pos = 0
    y_pos = height - square_size + 50

    cmd = [
        'ffmpeg',
        '-i', main_video,
        '-i', square_video,
        '-filter_complex',
        f'[1:v]scale={square_size}:{square_size}[small];[0:v][small]overlay={x_pos}:{y_pos}',
        '-c:a', 'copy',
        '-y',
        output_video
    ]

    subprocess.run(cmd, check=True)
    print(f"Результат наложения видео сохранен в {output_video}")

if __name__ == "__main__":
    overlay_videos_ffmpeg("main.mp4", "bao.mp4", "res.mp4")