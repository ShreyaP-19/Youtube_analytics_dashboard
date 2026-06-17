import sqlite3
import pandas as pd

DB_PATH = "database/youtube.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def top_videos_by_views(limit=10):
    conn = get_connection()
    query = """
    SELECT v.video_id, v.title, m.views
    FROM videos v
    JOIN video_metrics m ON v.video_id = m.video_id
    ORDER BY m.views DESC
    LIMIT ?;
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def top_videos_by_engagement(limit=10):
    conn = get_connection()
    query = """
    SELECT v.video_id, v.title, m.engagement_rate
    FROM videos v
    JOIN video_metrics m ON v.video_id = m.video_id
    ORDER BY m.engagement_rate DESC
    LIMIT ?;
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def top_like_rate(limit=10):
    conn = get_connection()
    query = """
    SELECT v.video_id, v.title, m.like_rate
    FROM videos v
    JOIN video_metrics m ON v.video_id = m.video_id
    ORDER BY m.like_rate DESC
    LIMIT ?;
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def top_comment_rate(limit=10):
    conn = get_connection()
    query = """
    SELECT v.video_id, v.title, m.comment_rate
    FROM videos v
    JOIN video_metrics m ON v.video_id = m.video_id
    ORDER BY m.comment_rate DESC
    LIMIT ?;
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def duration_vs_engagement():
    conn = get_connection()
    query = """
    SELECT v.duration, AVG(m.engagement_rate) as avg_engagement
    FROM videos v
    JOIN video_metrics m ON v.video_id = m.video_id
    GROUP BY v.duration
    ORDER BY avg_engagement DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def posting_trends():
    conn = get_connection()
    query = """
    SELECT substr(v.published, 1, 10) as date,
           COUNT(*) as videos_posted,
           AVG(m.views) as avg_views
    FROM videos v
    JOIN video_metrics m ON v.video_id = m.video_id
    GROUP BY date
    ORDER BY date;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df   

