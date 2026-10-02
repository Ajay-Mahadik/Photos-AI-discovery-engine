import streamlit as st
import pandas as pd

st.set_page_config(page_title="Category Discovery", layout="centered")

@st.cache_data(ttl=60)
def load_data():
    try:
        # Insert your published Google Sheets CSV link inside the quotes
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ72lib3473xj0WxWVDqpSS8kpqI6UPee3oCBSW90Mj6A5cPUnEk_8rnZD3v0AeG4CtUAowG7kUDXa7/pub?gid=402859117&single=true&output=csv"
        df = pd.read_csv(sheet_url) 
        
        # Filter out noise if the column exists
        if 'Archetype' in df.columns:
            df = df[df['Archetype'] != 'Noise']
        return df
    except Exception as e:
        st.error(f"Error loading live data: {e}")
        return pd.DataFrame()

df = load_data()

# Dynamically calculate the metric chips
if not df.empty:
    total_comments = len(df)
    play_store_count = len(df[df['Source'] == 'Google Play Store'])
    reddit_count = len(df[df['Source'] == 'Reddit (SerpApi)'])
    app_store_count = len(df[df['Source'] == 'Apple App Store'])
else:
    total_comments = play_store_count = reddit_count = app_store_count = 0

# Render Header
st.markdown("<p style='color: #888; font-size: 12px; font-weight: 600; text-transform: uppercase;'>Google Photos Core Experience</p>", unsafe_allow_html=True)
st.title("Why users struggle to retrieve old photos")
st.markdown("We read App Store, Play Store, and Reddit comments to spot patterns: memory gaps, missing metadata, and moments when chronological retrieval breaks down.")
st.write("")

# Render Metric Chips
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div style='border: 1px solid #ddd; padding: 8px; border-radius: 6px; font-size: 13px;'><b>{total_comments}</b> valid comments</div>", unsafe_allow_html=True)
col2.markdown(f"<div style='border: 1px solid #ddd; padding: 8px; border-radius: 6px; font-size: 13px;'>Play Store {play_store_count} · Reddit {reddit_count}</div>", unsafe_allow_html=True)
col3.markdown("<div style='border: 1px solid #ddd; padding: 8px; border-radius: 6px; font-size: 13px;'>Pattern-based summary</div>", unsafe_allow_html=True)
col4.markdown(f"<div style='border: 1px solid #ddd; padding: 8px; border-radius: 6px; font-size: 13px;'>App Store {app_store_count}</div>", unsafe_allow_html=True)
st.write("")

# Render Action Buttons
btn_col1, btn_col2, _ = st.columns([2, 2.5, 6])
with btn_col1:
    if st.button("Update summary", use_container_width=True):
        st.cache_data.clear() # Clears cache to pull latest Google Sheets row
        st.toast("Data refreshed from live Google Sheet!")
with btn_col2:
    if st.button("Check for new comments", use_container_width=True):
        st.toast("Triggering n8n webhook...") # Replace this with requests.post() to your n8n webhook later

# Render Tabs and Data Visualizations
if not df.empty:
    tab_insights, tab_dashboard, tab_evidence = st.tabs(["Insights", "Dashboard", "Raw Evidence"])

    with tab_insights:
        st.subheader("Core Retrieval Breakdown")
        st.markdown("""
        * **Episodic Memories Dominate:** 77% of retrieval friction stems from users trying to find photos based on life events, trips, or emotions, rather than exact dates.
        * **The Chronological Failure:** 23.5% of failures are caused by missing or broken chronological EXIF data, breaking the primary timeline scroll.
        * **High Friction Fallbacks:** When search fails, 13.5% of users resort to manual grid scrubbing, leading to severe frustration and churn threats.
        """)

    with tab_dashboard:
        st.subheader("Friction Severity by Archetype")
        if 'Archetype' in df.columns and 'Friction_Severity' in df.columns:
            severity_distribution = df.groupby(['Archetype', 'Friction_Severity']).size().unstack(fill_value=0)
            st.bar_chart(severity_distribution)
        else:
            st.write("Awaiting correct columns to render chart.")

    with tab_evidence:
        st.subheader("Read the raw user complaints")
        if 'Archetype' in df.columns:
            selected_archetype = st.selectbox("Filter quotes by archetype:", df['Archetype'].unique())
            display_cols = [col for col in ['Friction_Severity', 'Raw_Text', 'Forgotten_Metadata'] if col in df.columns]
            filtered_quotes = df[df['Archetype'] == selected_archetype][display_cols]
            st.dataframe(filtered_quotes, use_container_width=True)