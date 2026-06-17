-- Channels table
CREATE TABLE IF NOT EXISTS channels (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT,
    subscribers INTEGER,
    total_views INTEGER,
    total_videos INTEGER
);

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT,
    title TEXT,
    published TEXT,
    duration TEXT,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);

-- Video metrics table
CREATE TABLE IF NOT EXISTS video_metrics (
    video_id TEXT PRIMARY KEY,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    like_rate REAL,
    comment_rate REAL,
    engagement_rate REAL,
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
);
