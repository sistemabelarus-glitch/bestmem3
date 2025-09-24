name: Run Shorts Script

on:
  schedule:
    - cron: "0 */12 * * *"  # каждые 5 часов
  workflow_dispatch:  
  
permissions:
  contents: write  # ✅ даём права на запись в репо

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Клонируем репозиторий
        uses: actions/checkout@v3

      - name: 🐍 Устанавливаем Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: 📦 Устанавливаем зависимости
        run: |
          pip install -r requirements.txt

      - name: 🚀 Запускаем скрипт
        run: |
          python add_video.py

      - name: 💾 Коммитим обновлённую базу
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add videos.db
          git commit -m "Обновление базы видео [skip ci]" || echo "Нет изменений"
          git push
