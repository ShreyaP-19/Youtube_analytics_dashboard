import os
from fpdf import FPDF
import plotly.express as px
import pandas as pd
from datetime import datetime
from unidecode import unidecode

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 15, "YouTube Channel Analytics Report", border=0, ln=1, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_report(channel_name, metrics, df):
    """
    Generate a highly condensed 5-page PDF report per exact user specifications.
    """
    temp_dir = "temp_reports"
    os.makedirs(temp_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Image Paths
    path_top_bar = os.path.join(temp_dir, f"bar_{timestamp}.png")
    path_scatter = os.path.join(temp_dir, f"scatter_{timestamp}.png")
    path_hist_view = os.path.join(temp_dir, f"hview_{timestamp}.png")
    path_hist_eng = os.path.join(temp_dir, f"heng_{timestamp}.png")
    path_freq = os.path.join(temp_dir, f"freq_{timestamp}.png")
    path_trend = os.path.join(temp_dir, f"trend_{timestamp}.png")
    path_eng_bar = os.path.join(temp_dir, f"eb_{timestamp}.png")
    
    # Clean up titles for the chart axis natively (shortened to 40 chars max)
    w_df = df.copy()
    w_df['clean_title'] = w_df['title'].apply(lambda x: unidecode(str(x))[:40] + ('...' if len(str(x)) > 40 else ''))

    # 1. Generate All Temp Images
    # Dashboard Home - Top Videos
    top_vids = w_df.sort_values(by="views", ascending=False).head(10)
    fig_bar = px.bar(
        top_vids, x="views", y="clean_title", orientation="h",
        color="views", color_continuous_scale=["#93c5fd", "#3b82f6", "#1e3a8a"],
        title="Top 10 Highest Viewed Videos"
    )
    fig_bar.update_layout(
        yaxis={'categoryorder':'total ascending', 'title': None}, 
        margin=dict(l=250, r=20, t=40, b=20)   # Large left margin for titles
    )
    fig_bar.write_image(path_top_bar, width=1000, height=450, scale=2)

    # Video Performance - Scatter
    fig_scatter = px.scatter(
        w_df, x="views", y="engagement_rate", size="likes", color="comments",
        color_continuous_scale="Viridis", title="Reach vs. Engagement Matrix",
        labels={'views': 'View Count', 'engagement_rate': 'Engagement %'}
    )
    fig_scatter.write_image(path_scatter, width=1000, height=450, scale=2)

    # Video Performance - Histograms (Make them larger for the user)
    fig_hist_v = px.histogram(w_df, x="views", nbins=30, color_discrete_sequence=['#3b82f6'], title="View Distribution")
    fig_hist_v.write_image(path_hist_view, width=1000, height=450, scale=2)
    
    fig_hist_e = px.histogram(w_df, x="engagement_rate", nbins=30, color_discrete_sequence=['#10b981'], title="Engagement Distribution")
    fig_hist_e.write_image(path_hist_eng, width=1000, height=450, scale=2)

    # Growth Trends
    w_df['published'] = pd.to_datetime(w_df['published'])
    # NEW: Post Frequency Histogram
    w_df['publish_month'] = w_df['published'].dt.to_period('M').dt.start_time
    fig_freq = px.histogram(w_df, x="publish_month", title="Post Frequency Over Time", color_discrete_sequence=['#8b5cf6'])
    fig_freq.update_layout(xaxis_title="Publish Date", yaxis_title="Number of Videos")
    fig_freq.write_image(path_freq, width=1000, height=450, scale=2)

    df_trend = w_df.groupby(w_df['published'].dt.date).agg({'views': 'sum'}).reset_index()
    fig_trend = px.line(df_trend, x="published", y="views", line_shape="spline", color_discrete_sequence=['#f59e0b'], title="Viewing Momentum Over Time")
    fig_trend.write_image(path_trend, width=1000, height=450, scale=2)

    # Engagement Insights
    top_eng = w_df.sort_values(by="engagement_rate", ascending=False).head(10)
    fig_eng_bar = px.bar(
        top_eng, x="engagement_rate", y="clean_title", orientation="h",
        color="engagement_rate", color_continuous_scale=["#8b5cf6", "#d946ef", "#f43f5e"],
        title="Top 10 Most Engaging Videos"
    )
    fig_eng_bar.update_layout(
        yaxis={'categoryorder':'total ascending', 'title': None},
        margin=dict(l=250, r=20, t=40, b=20)
    )
    fig_eng_bar.write_image(path_eng_bar, width=1000, height=450, scale=2)


    # 2. Build the PDF
    pdf = PDFReport()
    pdf.set_margins(10, 10, 10)
    
    # ---------------- PAGE 1: Header, Channel Info, Core Metrics, & Top Viewed Content ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 24)
    pdf.cell(None, 15, "Executive Summary", ln=1, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", size=12)
    pdf.cell(None, 8, f"Channel Name: {unidecode(channel_name)}", ln=1)
    pdf.cell(None, 8, f"Report Date: {datetime.now().strftime('%B %d, %Y')}", ln=1)
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(None, 10, "Core Metrics", ln=1)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(None, 8, f"- Total Subscribers: {metrics.get('subscribers', 0):,}", ln=1)
    pdf.cell(None, 8, f"- Total Videos Analyzed: {metrics.get('videos', 0):,}", ln=1)
    pdf.cell(None, 8, f"- Total Lifetime Views: {metrics.get('views', 0):,}", ln=1)
    pdf.cell(None, 8, f"- Average Engagement Rate: {metrics.get('avg_engagement', 0.0):.2%}", ln=1)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(None, 10, "Highest Viewed Content", ln=1)
    pdf.image(path_top_bar, x=5, w=200)
    

    # ---------------- PAGE 2: Channel Analytics Metrics & Video Table ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(None, 12, "Channel Analytics Deep Dive", ln=1)
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(None, 10, "Performance Distribution:", ln=1)
    pdf.set_font("Helvetica", size=12)
    avg_views = int(w_df['views'].mean()) if not w_df.empty else 0
    peak_reach = int(w_df['views'].max()) if not w_df.empty else 0
    total_likes = int(w_df['likes'].sum()) if not w_df.empty else 0
    total_comments = int(w_df['comments'].sum()) if not w_df.empty else 0

    pdf.cell(None, 8, f"- Average Views per Video: {avg_views:,}", ln=1)
    pdf.cell(None, 8, f"- Peak Viral Reach (Max Views): {peak_reach:,}", ln=1)
    pdf.cell(None, 8, f"- Total Channel Likes: {total_likes:,}", ln=1)
    pdf.cell(None, 8, f"- Total Channel Comments: {total_comments:,}", ln=1)
    pdf.cell(None, 8, f"- Total Interactions (Likes + Comments): {(total_likes + total_comments):,}", ln=1)
    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(None, 10, "Top 5 Videos Data Table", ln=1)
    pdf.set_font("Helvetica", 'B', 10)
    
    # Simple Table Header
    pdf.cell(110, 8, "Video Title", border=1)
    pdf.cell(30, 8, "Views", border=1, align="R")
    pdf.cell(25, 8, "Likes", border=1, align="R")
    pdf.cell(25, 8, "Eng. %", border=1, align="R")
    pdf.ln()

    # Table Rows
    pdf.set_font("Helvetica", size=9)
    for _, row in top_vids.head(5).iterrows():
        title = unidecode(str(row['title']))[:50] + ('...' if len(str(row['title'])) > 50 else '')
        pdf.cell(110, 8, title, border=1)
        pdf.cell(30, 8, f"{int(row['views']):,}", border=1, align="R")
        pdf.cell(25, 8, f"{int(row['likes']):,}", border=1, align="R")
        pdf.cell(25, 8, f"{row['engagement_rate']:.2%}", border=1, align="R")
        pdf.ln()


    # ---------------- PAGE 3: Scatter Performance Chart & Engagement Intelligence ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(None, 12, "Video Performance Matrix", ln=1)
    pdf.image(path_scatter, x=5, w=200)
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(None, 12, "Engagement Intelligence", ln=1)
    pdf.image(path_eng_bar, x=5, w=200)


    # ---------------- PAGE 4: Post Frequency & Viewing Momentum ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(None, 12, "Growth Trends", ln=1)
    pdf.image(path_freq, x=5, w=200)
    pdf.ln(5)
    pdf.image(path_trend, x=5, w=200)


    # ---------------- PAGE 5: Performance Distributions ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(None, 12, "Performance Distributions", ln=1)
    pdf.image(path_hist_view, x=5, w=200)
    pdf.ln(5)
    pdf.image(path_hist_eng, x=5, w=200)


    # ---------------- PAGE 6: Strategic AI Insights & Recommendations ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(None, 12, "Strategic AI Insights", ln=1)
    pdf.ln(5)
    
    avg_eng = metrics.get('avg_engagement', 0.0)
    viral_vids = w_df[w_df['views'] > avg_views * 3]
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(None, 8, "Audience Retention:", ln=1)
    pdf.set_font("Helvetica", size=10)
    retention_text = "Your audience is exceptionally engaged. Focus on community-driven content." if avg_eng > 0.03 else "Engagement is within standard range. Consider adding more 'Call to Actions' in your videos."
    pdf.multi_cell(pdf.epw, 6, retention_text)
    pdf.ln(3)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(None, 8, "Growth Potential:", ln=1)
    pdf.set_font("Helvetica", size=10)
    growth_text = f"You have {len(viral_vids)} viral breakout videos. Analyze these topics for your next upload." if not viral_vids.empty else "Steady growth observed. No major viral breakouts yet. Keep experimenting with thumbnails and formats."
    pdf.multi_cell(pdf.epw, 6, growth_text)
    pdf.ln(3)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "Top Recommended Topics to Replicate:", ln=1)
    pdf.set_font("Helvetica", size=10)
    
    recommendations = w_df.sort_values(by="engagement_rate", ascending=False).head(4)['title'].tolist()
    for rec in recommendations:
        clean_title = unidecode(str(rec))
        # Ensure it fits on one line and forces a line break
        short_title = clean_title[:85] + "..." if len(clean_title) > 85 else clean_title
        pdf.cell(0, 8, f"- {short_title}", ln=1)

    # Output to pure bytes for Streamlit
    pdf_bytes = bytes(pdf.output(dest='S'))
    
    # Safely clear temp images
    for p in [path_top_bar, path_scatter, path_hist_view, path_hist_eng, path_freq, path_trend, path_eng_bar]:
        try: os.remove(p)
        except: pass
        
    return pdf_bytes
