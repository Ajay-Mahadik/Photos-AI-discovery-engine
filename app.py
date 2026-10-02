import streamlit as st
import pandas as pd
import requests

# 1. Page Configuration
st.set_page_config(page_title="Photos Discovery Engine", layout="centered")

# 2. Material Design 3 Custom CSS
st.markdown("""
<style>
.google-card {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    text-align: left;
    border: 1px solid #dadce0;
}
.google-metric {
    font-size: 28px;
    color: #1a73e8;
    font-weight: 500;
    margin-bottom: 4px;
    line-height: 1.2;
}
.google-label {
    font-size: 13px;
    color: #5f6368;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

# 3. Load Live Data from Google Sheets CSV
@st.cache_data(ttl=60)
def load_data():
    try:
        # REPLACE THIS LINK with your actual "Publish to Web" CSV link from Google Sheets
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ72lib3473xj0WxWVDqpSS8kpqI6UPee3oCBSW90Mj6A5cPUnEk_8rnZD3v0AeG4CtUAowG7kUDXa7/pub?gid=402859117&single=true&output=csv"
        df = pd.read_csv(sheet_url) 
        
        if 'Archetype' in df.columns:
            df = df[df['Archetype'] != 'Noise']
        return df
    except Exception as e:
        st.error(f"Error loading live data: {e}. Ensure you pasted the correct CSV link.")
        return pd.DataFrame()

df = load_data()

# 4. Dynamically Calculate Metrics
if not df.empty:
    total_comments = len(df)
    play_store_count = len(df[df['Source'] == 'Google Play Store'])
    reddit_count = len(df[df['Source'] == 'Reddit (SerpApi)'])
    app_store_count = len(df[df['Source'] == 'Apple App Store'])
else:
    total_comments = play_store_count = reddit_count = app_store_count = 0

# 5. Dashboard Header
st.markdown("<p style='color: #5f6368; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Google Photos Core Experience · Public Feedback</p>", unsafe_allow_html=True)
st.title("Why users struggle to retrieve old photos")
st.markdown("We read App Store, Play Store, and Reddit comments to spot patterns: memory gaps, missing metadata, and moments when chronological retrieval breaks down.")
st.write("")

# 6. Material Design Metric Cards
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='google-card'><div class='google-metric'>{total_comments}</div><div class='google-label'>Valid Logs</div></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='google-card'><div class='google-metric'>{play_store_count}</div><div class='google-label'>Play Store</div></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='google-card'><div class='google-metric'>{reddit_count}</div><div class='google-label'>Reddit</div></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='google-card'><div class='google-metric'>{app_store_count}</div><div class='google-label'>App Store</div></div>", unsafe_allow_html=True)
st.write("") 

# 7. Responsive Action Buttons
btn_col1, btn_col2, _ = st.columns([3, 4, 5])
with btn_col1:
    if st.button("Update summary", use_container_width=True):
        st.cache_data.clear()
        st.toast("Data refreshed from live Google Sheet!")
        st.rerun()
with btn_col2:
    if st.button("Check for new comments", type="primary", use_container_width=True):
        try:
            # If using ngrok to connect to local n8n, uncomment the line below and add your URL:
            # requests.post("https://YOUR-NGROK-URL.ngrok-free.app/webhook/episodic-search")
            st.toast("Triggering n8n pipeline...")
        except Exception as e:
            st.error("Could not reach the webhook.")

st.write("---")

# 8. Interactive Tabs
if not df.empty:
    tab_insights, tab_dashboard, tab_evidence = st.tabs(["Insights", "Dashboard", "Raw Evidence"])

    with tab_insights:
        st.markdown("<h3 style='color: #202124; font-size: 20px; font-weight: 500;'>Core Retrieval Breakdown</h3>", unsafe_allow_html=True)
        
        # Executive Insights
        st.markdown("""
        * **The Metadata Mismatch:** **23.5%** of failures stem from broken chronological EXIF data caused by third-party sharing (WhatsApp, AirDrop) overwriting original capture dates.
        * **Episodic Memories Dominate:** **77%** of retrieval friction stems from users trying to find these specific life events using visual or contextual memory, rather than exact transfer dates.
        * **The Compute & Churn Tax:** When search fails, **13.5%** of users resort to high-friction manual grid scrubbing, heavily taxing cloud compute infrastructure (thumbnail rendering) and degrading platform trust.
        """)
        
        st.write("---") 
        
        # Deep Dive Questions
        st.markdown("<h4 style='color: #202124; font-size: 18px; font-weight: 500;'>Deep Dive: The Episodic Memory Problem</h4>", unsafe_allow_html=True)
        st.write("We synthesized valid friction logs to diagnose the architectural gap between human memory and metadata-driven search:")
        st.write("")
        
        with st.expander("1. What kinds of old photos do users struggle to retrieve?"):
            st.write("Users primarily struggle with retrieving shared **Episodic Experiences (77.0%)**. These are specific life events (e.g., weddings, trips) where the user was present but received the media retroactively via third-party platforms like WhatsApp or AirDrop, breaking the continuity of their primary timeline.")
            
        with st.expander("2. What information do people actually remember about a photo?"):
            st.write("Users retain contextual, multi-variable visual anchors. The most common retained memories are visual characteristics (10.4%), co-occurring people/faces (10.2%), and emotional significance (8.2%). They remember the *cast of characters* and the *wardrobe/environment*, not the exact date the file was saved.")
            
        with st.expander("3. What information have they forgotten (or what metadata broke down)?"):
            st.write("The primary failure point is the **Metadata vs. Episodic Memory Mismatch** driven by chronological metadata failure (23.5%). When photos are downloaded via messaging apps, the original capture date is overwritten by the transfer date. The system indexes the photo in the wrong temporal cluster, rendering it invisible to chronological searches.")
            
        with st.expander("4. How do users formulate searches when their memory is incomplete?"):
            st.write("Users attempt broad, descriptive episodic searches (e.g., *'Goa trip with Rahul'*). Because current search architectures rigidly cross-reference keywords with localized EXIF temporal data, the system successfully finds the photos the user took natively, but completely filters out the visually related WhatsApp photos downloaded weeks later.")
            
        with st.expander("5. What are the most common fallback behaviors when search fails?"):
            st.write("The dominant fallback is high-friction manual timeline grid scrubbing (13.5%), followed by deep-diving into unorganized, local device folders like 'WhatsApp Images.' Users spend up to 30 minutes manually scanning for visual patterns because they no longer trust the search bar to handle temporal desyncs.")
            
        with st.expander("6. What is the business cost of these retrieval failures?"):
            st.write("The friction is severe, with **84.2% of all classified retrieval issues marked as High Severity**. When users are forced into manual 15-minute scrolling sessions, it heavily taxes cloud compute infrastructure (rendering thousands of thumbnails) and severely degrades user trust, pushing them to view the app as a dumping ground rather than an intelligent memory assistant.")
            
        with st.expander("7. Is this friction isolated to a specific operating system or cohort?"):
            st.write("No. While our primary data volume came from Android users (87.5%), this is a universal cross-platform failure. The friction is inherently driven by the interoperability of social sharing (e.g., iOS users AirDropping to Android, or WhatsApp compressing metadata globally), making it a universal structural flaw in how modern media is distributed.")
            
        with st.expander("8. What is the strategic opportunity area?"):
            st.write("Building the **Episodic AI Anchor**. Instead of relying on users to repair metadata or organize albums, the opportunity is deploying a visual semantic clustering engine. By evaluating multi-variable visual bridges (matching wardrobe, faces, and environment), the AI can confidently bypass broken EXIF transfer dates, dynamically grouping disjointed media back into its true original episode.")

    with tab_dashboard:
        st.markdown("<h3 style='color: #202124; font-size: 20px; font-weight: 500;'>Friction Severity by Archetype</h3>", unsafe_allow_html=True)
        if 'Archetype' in df.columns and 'Friction_Severity' in df.columns:
            severity_distribution = df.groupby(['Archetype', 'Friction_Severity']).size().unstack(fill_value=0)
            
            # Ensure logical column ordering if all columns exist
            if set(['High', 'Medium', 'Low']).issubset(severity_distribution.columns):
                severity_distribution = severity_distribution[['High', 'Medium', 'Low']]
                
            st.bar_chart(severity_distribution)
        else:
            st.warning("Awaiting correct columns to render chart.")

    with tab_evidence:
        st.markdown("<h3 style='color: #202124; font-size: 20px; font-weight: 500;'>Read the raw user complaints</h3>", unsafe_allow_html=True)
        if 'Archetype' in df.columns:
            selected_archetype = st.selectbox("Filter quotes by archetype:", df['Archetype'].unique())
            display_cols = [col for col in ['Friction_Severity', 'Raw_Text', 'Forgotten_Metadata', 'Fallback_Behavior'] if col in df.columns]
            filtered_quotes = df[df['Archetype'] == selected_archetype][display_cols]
            
            # Display dataframe taking full width
            st.dataframe(filtered_quotes, use_container_width=True, hide_index=True)
