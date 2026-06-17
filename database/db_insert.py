import sqlite3
import pandas as pd
import os
import json
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "youtube.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "clean_data.csv")
META_PATH = os.path.join(BASE_DIR, "data", "channel_meta.json")

# Connect to DB
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ---- Schema Enforcement ----
def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        channel_id TEXT PRIMARY KEY,
        channel_name TEXT,
        subscribers INTEGER,
        total_views INTEGER,
        total_videos INTEGER
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        channel_id TEXT,
        title TEXT,
        published TEXT,
        duration TEXT,
        views INTEGER,
        likes INTEGER,
        comments INTEGER,
        engagement_rate REAL,
        FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
    )
    """)
    conn.commit()

init_db()

# Load CSV
df = pd.read_csv(CSV_PATH)

# ---- Get Channel Metadata ----
channel_name = "Unknown Channel"
subscribers = 0
total_views = 0

if os.path.exists(META_PATH):
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
        channel_name = meta.get("channel_name", "Unknown Channel")
        subscribers = meta.get("subscribers", 0)
        total_views = meta.get("total_views", 0)

# ---- Insert Channel Data ----
channel_id = sys.argv[1] if len(sys.argv) > 1 else "DEFAULT_CHANNEL"

cursor.execute("""
INSERT OR REPLACE INTO channels
(channel_id, channel_name, subscribers, total_views, total_videos)
VALUES (?, ?, ?, ?, ?)
""", (
    channel_id,
    channel_name,
    subscribers,
    total_views,
    len(df)
))
print(f"DB: Updated channel record for: {channel_name} ({channel_id})")

# ---- Insert Videos ----
video_count = 0
for _, row in df.iterrows():
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO videos
        (video_id, channel_id, title, published, duration, views, likes, comments, engagement_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(row['video_id']),
            channel_id,
            str(row['title']),
            str(row['published']),
            str(row['duration']),
            int(row.get('views', 0)),
            int(row.get('likes', 0)),
            int(row.get('comments', 0)),
            float(row.get('engagement_rate', 0.0))
        ))
        video_count += 1
    except Exception as e:
        print(f"DB Warning: Failed to insert video {row.get('video_id')}: {e}")

print(f"DB: Successfully inserted/updated {video_count} videos.")


# Save changes
conn.commit()
conn.close()

print("OK: Data successfully inserted into SQLite database!")
