
# YouTube Analytics Dashboard

A comprehensive **Streamlit-based analytics dashboard** for YouTube channel performance evaluation and engagement analysis. This application provides detailed insights into video metrics, audience engagement, and channel performance through interactive visualizations and SQL-powered analytics.

---

## 🌐 Live Deployment
- **App**: [https://huggingface.co/spaces/ShreyaP1908/Youtube_analytics_dashboard](https://huggingface.co/spaces/ShreyaP1908/Youtube_analytics_dashboard)

## 📊 Features

- **Interactive Dashboard** - Real-time visualization of YouTube channel metrics
- **Video Performance Analytics** - Track views, likes, comments, and engagement rates
- **Engagement Analysis** - Compare videos by performance metrics
- **Channel Metrics** - Monitor subscriber growth and total channel views
- **Video Comparisons** - Side-by-side video performance analysis
- **Report Generation** - Create and export analytics reports
- **Database Management** - Persistent storage with SQLite
- **SQL Queries** - Pre-built analytical queries for custom insights

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.x |
| **Database** | SQLite3 |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly Express |
| **API Integration** | Google YouTube Data API v3 |
| **Configuration** | python-dotenv |

---

## 📁 Project Structure

```
youtube_analytics_project/
├── app.py                          # Main Streamlit application
├── main.py/                        # Package directory
├── README.md                       # This file
│
├── api/
│   └── youtube_api.py             # YouTube API data fetching & processing
│
├── analytics/
│   ├── sql_queries.py             # Pre-built SQL analytical queries
│   └── test_queries.py            # Query testing suite
│
├── database/
│   ├── db_connect.py              # Database connection handler
│   ├── db_insert.py               # Data insertion logic
│   ├── schema.sql                 # SQLite schema definitions
│   └── update_schema.py           # Schema migration utilities
│
├── pages/
│   └── comparison.py              # Video comparison page
│
├── utils/
│   ├── db_utils.py                # Database utility functions
│   └── report_generator.py        # Report generation logic
│
├── data/
│   ├── channel_meta.json          # Channel metadata (generated)
│   └── clean_data.csv             # Processed video data (generated)
│
└── temp_reports/                  # Temporary report files (generated)
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Google YouTube API Key
- Git

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd youtube_analytics_project
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```env
YOUTUBE_API_KEY=your_google_api_key_here
```

### Step 5: Initialize Database
```bash
python database/update_schema.py
```

---

## 📖 Usage

### Running the Dashboard
```bash
streamlit run app.py
```
The dashboard will open at `http://localhost:8501`

### Fetching YouTube Channel Data
```bash
python api/youtube_api.py <channel_id>
```
Replace `<channel_id>` with your target YouTube channel ID.

### Querying Analytics
```python
from analytics.sql_queries import top_videos_by_views, top_videos_by_engagement

# Get top 10 videos by views
top_views = top_videos_by_views(limit=10)

# Get top 10 videos by engagement
top_engagement = top_videos_by_engagement(limit=10)
```

---

## 🗄️ Database Schema

### `channels` Table
| Column | Type | Description |
|--------|------|-------------|
| `channel_id` | TEXT (PK) | Unique YouTube channel identifier |
| `channel_name` | TEXT | Channel name |
| `subscribers` | INTEGER | Subscriber count |
| `total_views` | INTEGER | Total channel views |
| `total_videos` | INTEGER | Total video count |

### `videos` Table
| Column | Type | Description |
|--------|------|-------------|
| `video_id` | TEXT (PK) | Unique YouTube video identifier |
| `channel_id` | TEXT (FK) | Associated channel ID |
| `title` | TEXT | Video title |
| `published` | TEXT | Publication date |
| `duration` | TEXT | Video duration |

### `video_metrics` Table
| Column | Type | Description |
|--------|------|-------------|
| `video_id` | TEXT (PK) | Associated video ID |
| `views` | INTEGER | View count |
| `likes` | INTEGER | Like count |
| `comments` | INTEGER | Comment count |
| `like_rate` | REAL | Likes per 1000 views |
| `comment_rate` | REAL | Comments per 1000 views |
| `engagement_rate` | REAL | Overall engagement percentage |

---

## 🔌 API Integration

The project uses the **Google YouTube Data API v3** to fetch:
- Channel information (subscribers, total views, video count)
- Video metadata (titles, duration, publication date)
- Video statistics (views, likes, comments)

### Getting a YouTube API Key
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create an API key credential
5. Add to `.env` file as `YOUTUBE_API_KEY`

---

## 📊 Key Analytics Queries

### Top Videos by Views
Returns the 10 most-viewed videos on the channel
```sql
SELECT v.video_id, v.title, m.views
FROM videos v
JOIN video_metrics m ON v.video_id = m.video_id
ORDER BY m.views DESC
LIMIT 10;
```

### Top Videos by Engagement
Returns videos ranked by engagement rate
```sql
SELECT v.video_id, v.title, m.engagement_rate
FROM videos v
JOIN video_metrics m ON v.video_id = m.video_id
ORDER BY m.engagement_rate DESC
LIMIT 10;
```

---

## 🔧 Configuration

Key configuration settings in `app.py`:
```python
DB_PATH = "database/youtube.db"          # SQLite database path
st.set_page_config(...)                  # Streamlit page settings
```

---

## 📝 Report Generation

Generate analytics reports:
```python
from utils.report_generator import create_report

report = create_report(video_data, metrics)
```

Reports are saved to `temp_reports/` directory.

---

## 🧪 Testing

Run query tests:
```bash
python analytics/test_queries.py
```

