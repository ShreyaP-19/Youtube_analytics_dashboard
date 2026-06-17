import streamlit as st
import pandas as pd
import sqlite3
import subprocess
import plotly.express as px

DB_PATH = "database/youtube.db"

st.set_page_config(page_title="Channel Comparison", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background Pattern - Soft and Distraction Free */
    .stApp {
        background-color: #f8fafc;
        background-image: 
            radial-gradient(at 0% 0%, #ffffff 0px, transparent 50%),
            radial-gradient(at 100% 0%, #fee2e2 0px, transparent 50%),
            radial-gradient(at 100% 100%, #f1f5f9 0px, transparent 50%),
            radial-gradient(at 0% 100%, #ffffff 0px, transparent 50%);
        background-attachment: fixed;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Main Content Container with Glassmorphism / White Card effect */
    .block-container {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 3rem !important;
        margin-top: 3rem !important;
        margin-bottom: 3rem !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.3);
        max-width: 90% !important;
    }

    /* Standardized Metric Card */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid #e2e8f0;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚔️ YouTube Channel Comparison")

# ---------------- INPUT SECTION ---------------- #

col1, col2 = st.columns(2)

with col1:
    st.subheader("Channel A")
    ch1 = st.text_input("Enter Channel ID (Channel A)", key="ch1")

with col2:
    st.subheader("Channel B")
    ch2 = st.text_input("Enter Channel ID (Channel B)", key="ch2")

# Fetch button
if st.button("Fetch & Compare Channels"):

    if ch1 and ch2:

        with st.spinner("Fetching channel data..."):
            subprocess.run(["python", "api/youtube_api.py", ch1])
            subprocess.run(["python", "database/db_insert.py", ch1])

            subprocess.run(["python", "api/youtube_api.py", ch2])
            subprocess.run(["python", "database/db_insert.py", ch2])

        st.success("Channels loaded!")

# ---------------- LOAD DATA ---------------- #

def load_data():
    conn = sqlite3.connect(DB_PATH)
    videos = pd.read_sql("SELECT * FROM videos", conn)
    channels = pd.read_sql("SELECT * FROM channels", conn)
    conn.close()
    return videos, channels

df, ch_df = load_data()

# Filter channel data
df1 = df[df["channel_id"] == ch1]
df2 = df[df["channel_id"] == ch2]

ch1_meta = ch_df[ch_df["channel_id"] == ch1]
ch2_meta = ch_df[ch_df["channel_id"] == ch2]

# ---------------- METRICS CALCULATION ---------------- #

def compute_metrics(df, meta):
    if df.empty:
        return None

    return {
        "videos": len(df),
        "views": df["views"].sum(),
        "avg_views": df["views"].mean(),
        "engagement": df["engagement_rate"].mean(),
        "likes": df["likes"].sum(),
        "comments": df["comments"].sum(),
        "subscribers": meta.iloc[0]["subscribers"] if not meta.empty else 0
    }

m1 = compute_metrics(df1, ch1_meta)
m2 = compute_metrics(df2, ch2_meta)

# ---------------- COMPARISON DASHBOARD ---------------- #

if m1 and m2:

    st.divider()
    st.header("📊 Performance Comparison")

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Channel A")
        st.metric("Subscribers", f"{m1['subscribers']:,}")
        st.metric("Total Videos", m1["videos"])
        st.metric("Total Views", f"{m1['views']:,}")
        st.metric("Average Views", f"{int(m1['avg_views']):,}")
        st.metric("Avg Engagement", f"{m1['engagement']:.2%}")
        st.metric("Total Likes", f"{m1['likes']:,}")
        st.metric("Total Comments", f"{m1['comments']:,}")

    with colB:
        st.subheader("Channel B")
        st.metric("Subscribers", f"{m2['subscribers']:,}")
        st.metric("Total Videos", m2["videos"])
        st.metric("Total Views", f"{m2['views']:,}")
        st.metric("Average Views", f"{int(m2['avg_views']):,}")
        st.metric("Avg Engagement", f"{m2['engagement']:.2%}")
        st.metric("Total Likes", f"{m2['likes']:,}")
        st.metric("Total Comments", f"{m2['comments']:,}")

# ---------------- WINNER ANALYSIS ---------------- #

    st.divider()
    st.header("🏆 Winner Analysis")

    def winner(a, b):
        return "Channel A" if a > b else "Channel B"

    st.write(f"**Higher Subscribers:** {winner(m1['subscribers'], m2['subscribers'])}")
    st.write(f"**More Total Views:** {winner(m1['views'], m2['views'])}")
    st.write(f"**Better Engagement:** {winner(m1['engagement'], m2['engagement'])}")
    st.write(f"**More Likes:** {winner(m1['likes'], m2['likes'])}")
    st.write(f"**More Comments:** {winner(m1['comments'], m2['comments'])}")
    st.write(f"**Higher Avg Views:** {winner(m1['avg_views'], m2['avg_views'])}")

# ---------------- VISUAL COMPARISON ---------------- #

    st.divider()
    st.header("📈 Visual Comparison")

    comp_df = pd.DataFrame({
        "Metric": ["Subscribers", "Total Views", "Avg Views", "Engagement", "Likes", "Comments"],
        "Channel A": [
            m1["subscribers"],
            m1["views"],
            m1["avg_views"],
            m1["engagement"],
            m1["likes"],
            m1["comments"]
        ],
        "Channel B": [
            m2["subscribers"],
            m2["views"],
            m2["avg_views"],
            m2["engagement"],
            m2["likes"],
            m2["comments"]
        ]
    })

    comp_df_melt = comp_df.melt(id_vars="Metric", var_name="Channel", value_name="Value")

    fig = px.bar(
        comp_df_melt,
        x="Metric",
        y="Value",
        color="Channel",
        barmode="group",
        title="Channel Performance Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- TOP VIDEOS COMPARISON ---------------- #

    st.divider()
    st.header("🔥 Top Videos Comparison")

    top1 = df1.sort_values("views", ascending=False).head(5)
    top2 = df2.sort_values("views", ascending=False).head(5)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Channel A Videos")
        st.dataframe(top1[["title", "views", "likes", "comments"]])

    with col2:
        st.subheader("Top Channel B Videos")
        st.dataframe(top2[["title", "views", "likes", "comments"]])

# ---------------- FINAL STRATEGIC INSIGHT ---------------- #

    st.divider()
    st.header("🧠 Strategic Insight")

    if m1["engagement"] > m2["engagement"]:
        st.info("Channel A has stronger audience engagement. Their content likely resonates better with viewers.")

    elif m2["engagement"] > m1["engagement"]:
        st.info("Channel B has stronger engagement. Their community interaction is higher.")

    else:
        st.info("Both channels have similar engagement levels.")
