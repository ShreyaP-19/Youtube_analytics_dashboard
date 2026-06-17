import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import subprocess
import shutil
import time
from datetime import datetime
from utils.report_generator import create_report


# ---------------- CONFIG ---------------- #
st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

DB_PATH = "database/youtube.db"

# Initialize Session State for "Fresh Start" behavior
if 'is_fresh' not in st.session_state:
    st.session_state.is_fresh = True

# ---------------- CUSTOM CSS (Clean & Standard) ---------------- #
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

    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 10px;
        background: -webkit-linear-gradient(45deg, #ff0000, #ff7f00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
    }

    /* Headers */
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 700;
    }

    .section-header {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.markdown("<div class='sidebar-title'>📊 YT Analytics Pro</div>", unsafe_allow_html=True)
    
    st.subheader("📡 Data Control")
    channel_id_input = st.text_input("YouTube Channel ID", placeholder="UCxxxxxxxxxxxx", help="Enter the unique ID of the YouTube channel you want to analyze.")
    
    if st.button("Fetch Channel Data", type="primary"):
        if channel_id_input.strip():
            with st.status("Initializing data pipeline...", expanded=True) as status:
                st.write("Extracting data from YouTube API...")
                api_process = subprocess.run(["python", "api/youtube_api.py", channel_id_input.strip()], capture_output=True, text=True)
                
                if api_process.returncode != 0:
                    status.update(label="API Extraction Failed", state="error", expanded=True)
                    st.error(f"YouTube API Error: {api_process.stderr}")
                    st.info("Check if the Channel ID is valid and your API Key is correctly configured in the .env file.")
                else:
                    st.write("Processing and storing data...")
                    db_process = subprocess.run(["python", "database/db_insert.py", channel_id_input.strip()], capture_output=True, text=True)
                    
                    if db_process.returncode != 0:
                        status.update(label="Database Insertion Failed", state="error", expanded=True)
                        st.error(f"Database Error: {db_process.stderr}")
                    else:
                        status.update(label="Data Load Complete!", state="complete", expanded=False)
                        st.session_state.is_fresh = False
                        st.success("Database updated.")
                        st.rerun()
        else:
            st.error("Please enter a Channel ID.")

    st.divider()
    st.subheader("🧭 Navigation")
    selection = st.radio(
        "Select Dashboard View",
        ["Dashboard Home", "Channel Analytics", "Video Performance", "Growth Trends", "Engagement Insights", "Data Explorer", "Strategic AI", "Executive Report", "About"]   
    )

    with st.sidebar:
        st.divider()
        st.subheader("⚔️ Channel Tools")

        if st.button("Compare Two Channels"):
            st.switch_page("pages/comparison.py")
    
# ---------------- HELPERS ---------------- #
def format_number(num):
    if num >= 1e9:
        return f"{num / 1e9:.2f}B"
    elif num >= 1e6:
        return f"{num / 1e6:.2f}M"
    elif num >= 1e3:
        return f"{num / 1e3:.2f}K"
    else:
        return f"{num:,}"

# ---------------- UTILS ---------------- #
def safe_remove(path, max_retries=10, delay=1.0):
    """
    Extremely robust removal for Windows.
    1. Tries normal removal.
    2. Tries deleting all files inside first.
    3. Tries renaming the directory before deletion (rename trick).
    4. Falls back to just clearing contents if the folder itself is locked.
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return True

    for i in range(max_retries):
        try:
            if os.path.isfile(path):
                os.remove(path)
                return True
            
            # If directory, try to empty it first
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for name in files:
                        try:
                            os.remove(os.path.join(root, name))
                        except:
                            pass
                    for name in dirs:
                        try:
                            os.rmdir(os.path.join(root, name))
                        except:
                            pass
                
                # Now try to remove the root dir
                try:
                    os.rmdir(path)
                    return True
                except OSError:
                    # Rename trick: move it to a temp name and try again
                    temp_path = f"{path}_old_{int(time.time())}"
                    try:
                        os.rename(path, temp_path)
                        shutil.rmtree(temp_path, ignore_errors=True)
                        return True
                    except:
                        pass
            
            # If we reach here, sth still locked. Try shutil as last resort for this iteration.
            shutil.rmtree(path)
            return True
            
        except PermissionError:
            if i < max_retries - 1:
                time.sleep(delay)
            else:
                # If it's a directory and still locked, we've at least cleared files.
                # Don't crash, just let the user know.
                if os.path.isdir(path):
                    return "partial" 
                raise
        except Exception:
            if i == max_retries - 1: raise
            time.sleep(delay)
    return False

# ---------------- DATA LOADER ---------------- #
def get_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM videos", conn)
        ch_df = pd.read_sql("SELECT * FROM channels", conn)
        conn.close()
        return df, ch_df
    except:
        return pd.DataFrame(), pd.DataFrame()

df, ch_df = get_data()

# Sidebar reset button
with st.sidebar:
    st.divider()
    if st.button("🗑️ Reset All Data", help="Permanently delete all local data and the database"):
        try:
            st.cache_data.clear()
            
            results = []
            if os.path.exists(DB_PATH):
                results.append(safe_remove(DB_PATH))
            if os.path.exists("data"):
                results.append(safe_remove("data"))
                
            if "partial" in results:
                st.warning("Data files were cleared, but the folders are currently locked by another process (likely Windows Indexing or Streamlit).")
                st.info("The next time you restart your computer or close Streamlit, these empty folders can be deleted manually.")
            else:
                st.success("All data cleared successfully.")
            
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Critical error clearing data: {e}")
            st.info("Tip: Close any open CSV files or the SQLite database in other programs (like Excel or DB Browser) and try again.")

# ---------------- DASHBOARD LOGIC ---------------- #

if ch_df.empty or st.session_state.get('is_fresh', True):
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 4rem; font-weight: 800; background: -webkit-linear-gradient(45deg, #ff0000, #ff7f00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem;">
            YouTube Analytics Pro
        </h1>
        <p style="font-size: 1.5rem; color: #64748b; font-weight: 500;">
            Unlock the power of your channel's data with advanced analytics and AI insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("👈 Please enter a YouTube Channel ID in the sidebar to get started.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: #ffffff; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center; height: 100%;">
            <h1 style="font-size: 3rem; margin: 0;">📊</h1>
            <h3 style="margin-top: 1rem; color: #1e293b;">Deep Analytics</h3>
            <p style="color: #64748b; font-size: 1rem;">Comprehensive subscription, view, and engagement metrics.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: #ffffff; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center; height: 100%;">
            <h1 style="font-size: 3rem; margin: 0;">📈</h1>
            <h3 style="margin-top: 1rem; color: #1e293b;">Growth Trends</h3>
            <p style="color: #64748b; font-size: 1rem;">Visualize your progress and viewing momentum over time.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: #ffffff; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center; height: 100%;">
            <h1 style="font-size: 3rem; margin: 0;">🤖</h1>
            <h3 style="margin-top: 1rem; color: #1e293b;">Smart Insights</h3>
            <p style="color: #64748b; font-size: 1rem;">AI recommendations to boost reach.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not ch_df.empty:
        st.divider()
        if st.button("🚀 Continue to Dashboard", type="primary", use_container_width=True):
            st.session_state.is_fresh = False
            st.rerun()
    st.stop()

# Helper for Channel Selection
with st.sidebar:
    st.divider()
    st.subheader("📺 Switch Channel")

    if not ch_df.empty:
        channel_options = {
            f"{row['channel_name']} ({row['channel_id'][:8]}...)": row['channel_id']
            for _, row in ch_df.iterrows()
        }

        default_index = len(channel_options) - 1

        selected_display_name = st.selectbox(
            "Select Channel to View",
            options=list(channel_options.keys()),
            index=default_index,
            on_change=lambda: st.session_state.update(is_fresh=False)
        )

        selected_channel_id = channel_options[selected_display_name]
        selected_channel_name = selected_display_name.split(" (")[0]
    else:
        selected_channel_id = None
        selected_channel_name = "No Channel Selected"

# Filter Data for Selected Channel
if selected_channel_id:
    filtered_df = df[df['channel_id'] == selected_channel_id].copy()
else:
    filtered_df = pd.DataFrame()

with st.sidebar:
    st.divider()
    st.subheader("🔎 Advanced Filters")

    if not filtered_df.empty:

        # Safety check: slider max_value must be > min_value
        max_v = int(filtered_df['views'].max())
        min_views = st.slider(
            "Minimum Views",
            min_value=0,
            max_value=max(max_v, 1),
            value=0
        )

        max_e = float(filtered_df['engagement_rate'].max())
        min_engagement = st.slider(
            "Minimum Engagement Rate",
            min_value=0.0,
            max_value=max(max_e, 0.01),
            value=0.0
        )

        date_range = st.date_input("Filter by Publish Date", [])

    else:
        min_views = 0
        min_engagement = 0.0
        date_range = []

# ---------------- APPLY GLOBAL FILTERS ---------------- #

if not filtered_df.empty:

    filtered_df = filtered_df[filtered_df['views'] >= min_views]

    filtered_df = filtered_df[
        filtered_df['engagement_rate'] >= min_engagement
    ]

    if len(date_range) == 2:
        filtered_df['published'] = pd.to_datetime(filtered_df['published']).dt.tz_localize(None)
        filtered_df = filtered_df[
            (filtered_df['published'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['published'] <= pd.to_datetime(date_range[1]))
        ]

selected_ch_meta = ch_df[ch_df['channel_id'] == selected_channel_id]

if not selected_ch_meta.empty:
    selected_ch_meta = selected_ch_meta.iloc[0]
else:
    selected_ch_meta = None
# --- 1. Dashboard Home ---
if selection == "Dashboard Home":
    st.markdown(f"<div class='section-header'><h1>🏠 Dashboard Overview: {selected_channel_name}</h1></div>", unsafe_allow_html=True)
    
    if filtered_df.empty:
        st.warning(f"No video data found for {selected_channel_name}.")
    else:
        m1, m2, m3, m4, m5 = st.columns(5)
        total_videos = len(filtered_df)
        total_views = filtered_df["views"].sum()
        avg_eng = filtered_df["engagement_rate"].mean()
        total_likes = filtered_df["likes"].sum()
        subscribers = selected_ch_meta['subscribers'] if selected_ch_meta is not None else 0

        m1.metric("Subscribers", format_number(subscribers))
        m2.metric("Total Videos", format_number(total_videos))
        m3.metric("Total Views", format_number(total_views))
        m4.metric("Avg Engagement", f"{avg_eng:.2%}")
        m5.metric("Total Likes", format_number(total_likes))

        st.markdown("### 🔥 Top Performing Videos")
        top_vids = filtered_df.sort_values(by="views", ascending=False).head(10)
        
        fig = px.bar(
            top_vids, x="views", y="title", orientation="h",
            color="views", color_continuous_scale=["#93c5fd", "#3b82f6", "#1e3a8a"],
            labels={'views': 'Total Views', 'title': 'Video Title'},
            height=500
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Download Report Section
        st.divider()
        st.markdown("### 📥 Export Channel Report")
        
        @st.cache_data(show_spinner=False)
        def cache_pdf(ch_name, s, v, vi, e, data_bytes):
            import pandas as pd
            import io
            metrics = {
                'subscribers': s,
                'views': v,
                'videos': vi,
                'avg_engagement': e
            }
            # Unpack bytes back to df (prevents hashing issues in cache)
            _df = pd.read_csv(io.BytesIO(data_bytes))
            return create_report(ch_name, metrics, _df)

        with st.spinner("Preparing report for download..."):
            df_csv = filtered_df.to_csv(index=False).encode('utf-8')
            try:
                pdf_data = cache_pdf(selected_channel_name, subscribers, total_views, total_videos, avg_eng, df_csv)
                
                st.download_button(
                    label="📄 Download Report PDF",
                    data=bytes(pdf_data),
                    file_name=f"{selected_channel_name.replace(' ', '_')}_Report.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Generation Error: {e}")

# --- 2. Channel Analytics ---
elif selection == "Channel Analytics":
    st.markdown(f"<div class='section-header'><h1>📡 Channel Deep Dive: {selected_channel_name}</h1></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Performance Metrics")
        st.write(f"**Total Videos:** {len(filtered_df)}")
        st.write(f"**Total Views:** {filtered_df['views'].sum():,}")
        st.write(f"**Average Views per Video:** {int(filtered_df['views'].mean()):,}")
        st.write(f"**Peak Viral Reach:** {filtered_df['views'].max():,}")

    with col2:
        st.subheader("Engagement Distribution")
        st.write(f"**Average Engagement Rate:** {filtered_df['engagement_rate'].mean():.2%}")
        st.write(f"**Total Interactions (L+C):** {int(filtered_df['likes'].sum() + filtered_df['comments'].sum()):,}")

    st.divider()
    st.subheader("Video Metadata Explorer")
    st.dataframe(filtered_df[["title", "views", "likes", "comments", "engagement_rate"]].sort_values(by="views", ascending=False), use_container_width=True)

# --- 3. Video Performance ---
elif selection == "Video Performance":
    st.markdown(f"<div class='section-header'><h1>🎥 Video Performance Matrix: {selected_channel_name}</h1></div>", unsafe_allow_html=True)
    
    # Clean data to avoid JSON serialization errors with NaN/Inf/0 values in Plotly size
    cleaned_df = filtered_df.copy()
    cleaned_df['views'] = pd.to_numeric(cleaned_df['views'], errors='coerce').fillna(0)
    cleaned_df['engagement_rate'] = pd.to_numeric(cleaned_df['engagement_rate'], errors='coerce').fillna(0)
    cleaned_df['likes'] = pd.to_numeric(cleaned_df['likes'], errors='coerce').fillna(0)
    cleaned_df['comments'] = pd.to_numeric(cleaned_df['comments'], errors='coerce').fillna(0)
    
    # Replace Inf with 0
    cleaned_df = cleaned_df.replace([float('inf'), float('-inf')], 0)
    
    # Plotly's `size` cannot be 0 or negative; forcefully handle it 
    # to avoid the Javascript JSON array serialization bug in Streamlit
    cleaned_df['plot_size'] = cleaned_df['likes'].apply(lambda x: max(1, x))

    fig = px.scatter(
        cleaned_df, x="views", y="engagement_rate", 
        size="plot_size", color="comments",
        hover_name="title",
        labels={'views': 'View Count', 'engagement_rate': 'Engagement %'},
        title="Reach vs. Engagement Matrix",
        color_continuous_scale="Viridis",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### View Distribution")
        fig_hist = px.histogram(filtered_df, x="views", nbins=30, color_discrete_sequence=['#3b82f6'])
        st.plotly_chart(fig_hist, use_container_width=True)
    with col2:
        st.markdown("### Engagement Distribution")
        fig_eng = px.histogram(filtered_df, x="engagement_rate", nbins=30, color_discrete_sequence=['#10b981'])
        st.plotly_chart(fig_eng, use_container_width=True)

# --- 4. Growth Trends ---
elif selection == "Growth Trends":
    st.markdown(f"<div class='section-header'><h1>📈 Content & Growth Trends: {selected_channel_name}</h1></div>", unsafe_allow_html=True)
    
    # Use a copy to avoid SettingWithCopyWarning
    trends_df = filtered_df.copy()
    if filtered_df.empty:
        st.warning("No data available for trend analysis.")
        st.stop()
    trends_df['published'] = pd.to_datetime(trends_df['published'])
    df_trend = trends_df.groupby(trends_df['published'].dt.date).agg({
        'title': 'count',
        'views': 'sum'
    }).reset_index()
    df_trend.columns = ['Date', 'Videos Posted', 'Daily Views']

    st.subheader("Post Frequency Over Time")
    fig1 = px.area(df_trend, x="Date", y="Videos Posted", line_shape="spline", color_discrete_sequence=['#3b82f6'])
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Viewing Momentum")
    fig2 = px.line(df_trend, x="Date", y="Daily Views", line_shape="spline", color_discrete_sequence=['#f59e0b'])
    st.plotly_chart(fig2, use_container_width=True)

# --- 5. Engagement Insights ---
elif selection == "Engagement Insights":
    st.markdown(f"<div class='section-header'><h1>💎 Engagement Intelligence: {selected_channel_name}</h1></div>", unsafe_allow_html=True)
    
    top_eng = filtered_df.sort_values(by="engagement_rate", ascending=False).head(15)
    
    fig = px.bar(
        top_eng, x="engagement_rate", y="title", orientation="h",
        color="engagement_rate", color_continuous_scale=["#8b5cf6", "#d946ef", "#f43f5e"],
        labels={'engagement_rate': 'Engagement Rate', 'title': 'Video Title'},
        height=600
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# --- 6. Data Explorer ---
elif selection == "Data Explorer":
    st.markdown(f"<div class='section-header'><h1>📋 Raw Data Explorer: {selected_channel_name}</h1></div>", unsafe_allow_html=True)
    
    search = st.text_input("Search Video Titles", "")
    final_filtered = filtered_df[filtered_df['title'].str.contains(search, case=False, na=False)]
    
    st.dataframe(final_filtered, use_container_width=True)
    
    csv = final_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Export Results to CSV",
        csv,
        f"youtube_data_{selected_channel_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        key='download-csv'
    )

# --- 7. Strategic AI ---
elif selection == "Strategic AI":
    st.markdown(f"<div class='section-header'><h1>🤖 Strategic Intelligence Engine: {selected_channel_name}</h1></div>", unsafe_allow_html=True)
    
    avg_views = filtered_df['views'].mean()
    avg_eng = filtered_df['engagement_rate'].mean()
    
    st.subheader("Key Takeaways")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.info("🎯 **Audience Retention**")
        if avg_eng > 0.03:
            st.write("Your audience is exceptionally engaged. Focus on community-driven content.")
        else:
            st.write("Engagement is within standard range. Consider adding more 'Call to Actions' in your videos.")

    with c2:
        st.info("🚀 **Growth Potential**")
        viral_vids = filtered_df[filtered_df['views'] > avg_views * 3]
        if not viral_vids.empty:
            st.write(f"You have {len(viral_vids)} viral breakout videos. Analyze these topics for your next upload.")
        else:
            st.write("Steady growth observed. No major viral breakouts yet—keep experimenting with thumbnails.")

    st.divider()
    st.markdown("### Top Recommended Topics")
    st.write("Based on your top 5 highest engagement videos:")
    recommendations = filtered_df.sort_values(by="engagement_rate", ascending=False).head(5)['title'].tolist()
    for rec in recommendations:
        st.write(f"- {rec}")

# --- 8. Executive Report ---
elif selection == "Executive Report":
    st.markdown(f"<div class='section-header'><h1>📄 Executive Summary: {selected_channel_name}</h1></div>", unsafe_allow_html=True)
    
    with st.expander("System Overview", expanded=True):
        st.markdown(f"""
        **Channel Name:** {selected_channel_name}  
        **Report Date:** {datetime.now().strftime('%B %d, %Y')}
        **Total Reach:** {filtered_df['views'].sum():,} views
        **Library Size:** {len(filtered_df)} videos
        
        This dashboard provides a comprehensive analysis of the identified YouTube channel using automated extraction via YouTube API v3 and processing through a persistent SQL backend.
        """)
    
    with st.expander("Strategic Recommendations", expanded=True):
        st.markdown("""
        - **Optimize Underperforming Content**: Identify videos with low engagement and update metadata.
        - **Leverage Viral Success**: Replicate formats and topics from high-view videos.
        - **Consistent Posting**: Maintain posting frequency to improve algorithmic reach.
        """)

# --- 9. About ---
elif selection == "About":
    st.markdown("<div class='section-header'><h1>ℹ️ About YT Analytics Pro</h1></div>", unsafe_allow_html=True)
    
    st.markdown("""
    ### Technical Specification
    - **Frontend**: Streamlit (Standard Professional UI)
    - **Processing**: Pandas & NumPy
    - **Database**: SQLite3
    - **API**: YouTube Data API v3
    - **Visualization**: Plotly Graphing Libraries
    
    Developed for high-scale performance analysis and channel intelligence.
    """)
    st.divider()
    st.caption("© 2026 YouTube Analytics Pro • Standard Edition")
