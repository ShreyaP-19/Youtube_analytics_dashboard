import os
import sys
import json
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CSV_PATH = "data/clean_data.csv"
META_PATH = "data/channel_meta.json"

if not API_KEY:
    print("ERROR: YOUTUBE_API_KEY not found in .env file.")
    sys.exit(1)

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Cleanup old data to prevent stale re-insertion
if os.path.exists(CSV_PATH):
    os.remove(CSV_PATH)
if os.path.exists(META_PATH):
    os.remove(META_PATH)

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_info(channel_id):
    try:
        request = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        )
        return request.execute()
    except Exception as e:
        print(f"ERROR: API Error fetching channel info: {e}")
        sys.exit(1)

if len(sys.argv) < 2:
    print("ERROR: Channel ID argument missing.")
    sys.exit(1)

channel_id = sys.argv[1]
data = get_channel_info(channel_id)

if not data.get('items'):
    print(f"ERROR: No channel found with ID: {channel_id}")
    sys.exit(1)

item = data['items'][0]
channel_data = {
    "channel_name": item['snippet']['title'],
    "subscribers": item['statistics'].get('subscriberCount', 0),
    "total_views": item['statistics'].get('viewCount', 0),
    "total_videos": item['statistics'].get('videoCount', 0),
    "uploads_playlist": item['contentDetails']['relatedPlaylists']['uploads']
}

print(f"OK: Found Channel: {channel_data['channel_name']}")

def get_video_ids(playlist_id):
    video_ids = []
    try:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )

        while request:
            response = request.execute()
            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])
            request = youtube.playlistItems().list_next(request, response)
    except Exception as e:
        print(f"ERROR: API Error fetching video IDs: {e}")
        sys.exit(1)

    return video_ids

video_ids = get_video_ids(channel_data["uploads_playlist"])
if not video_ids:
    print("WARNING: No videos found in the uploads playlist.")
    # Create empty CSV so db_insert doesn't fail, but maybe it should fail?
    # Let's write an empty CSV with columns anyway
    pd.DataFrame(columns=["video_id", "title", "published", "views", "likes", "comments", "duration", "engagement_rate"]).to_csv(CSV_PATH, index=False)
    with open(META_PATH, "w") as f:
        json.dump(channel_data, f)
    sys.exit(0)

def get_video_details(video_ids):
    all_data = []
    try:
        for i in range(0, len(video_ids), 50):
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(video_ids[i:i+50])
            )
            response = request.execute()

            for video in response['items']:
                data = {
                    "video_id": video['id'],
                    "title": video['snippet']['title'],
                    "published": video['snippet']['publishedAt'],
                    "views": int(video['statistics'].get('viewCount', 0)),
                    "likes": int(video['statistics'].get('likeCount', 0)),
                    "comments": int(video['statistics'].get('commentCount', 0)),
                    "duration": video['contentDetails']['duration']
                }
                all_data.append(data)
    except Exception as e:
        print(f"ERROR: API Error fetching video details: {e}")
        sys.exit(1)
    return all_data

videos_data = get_video_details(video_ids)
df = pd.DataFrame(videos_data)
df.fillna(0, inplace=True)
df.drop_duplicates(subset="video_id", inplace=True)

# Metrics
df['engagement_rate'] = (df['likes'] + df['comments']) / df['views'].replace(0, 1)

# Save data
df.to_csv(CSV_PATH, index=False)
with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(channel_data, f)

print(f"OK: Successfully fetched data for {len(videos_data)} videos.")
