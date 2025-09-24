import sqlite3

# --- Функция для инициализации базы ---
def init_db(db_name="videos.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT UNIQUE,
        status TEXT DEFAULT 'new',  -- new | downloaded | processed
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


# --- Функция для добавления video_id ---
def save_video_id(video_id, db_name="videos.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO videos (video_id, status) VALUES (?, 'new')", (video_id,))
        conn.commit()
        print(f"✅ Новый video_id сохранён: {video_id}")
        result = True
    except sqlite3.IntegrityError:
        print(f"⏭ video_id уже есть в базе: {video_id}")
        result = False

    conn.close()
    return result


# --- Функция для получения всех сохранённых video_id (при желании) ---
def get_all_video_ids(db_name="videos.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT video_id, status, added_at FROM videos ORDER BY added_at DESC")
    rows = cursor.fetchall()
    conn.close()
    # Возвращаем как список словарей
    return [
        {
            "video_id": r[0],
            "status": r[1],
            "added_at": r[2] if isinstance(r[2], str) else datetime.fromtimestamp(r[2]).isoformat()
        }
        for r in rows
    ]

def update_video_status(video_id, status, db_name="videos.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("UPDATE videos SET status=? WHERE video_id=?", (status, video_id))
    conn.commit()
    conn.close()
    print(f"🔄 Статус {video_id} обновлён на '{status}'")
