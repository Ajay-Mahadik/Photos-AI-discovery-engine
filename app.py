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
        
        # Original Executive Insights
        st.markdown("""
        * **Episodic Memories Dominate:** **77%** of retrieval friction stems from users trying to find photos based on life events, trips, or emotions, rather than exact dates.
        * **The Chronological Failure:** **23.5%** of failures are caused by missing or broken chronological EXIF data, breaking the primary timeline scroll.
        * **High Friction Fallbacks:** When search fails, **13.5%** of users resort to manual grid scrubbing, leading to severe frustration and churn threats.
        """)
        
        st.write("---")
        
        # Deep Dive Questions
        st.markdown("<h4 style='color: #202124; font-size: 18px; font-weight: 500;'>Deep Dive: Discovery Questions</h4>", unsafe_allow_html=True)
        st.write("We synthesized the user friction logs to answer the core discovery questions for the NextLeap PM project:")
        st.write("")
        
        with st.expander("1. What kinds of old photos do users struggle to retrieve?"):
            st.write("Users primarily struggle with **Episodic Experiences (77.0%)**. These are specific family milestones, travel memories, or emotional moments where the user remembers the *context* of the photo, but lacks the exact technical identifiers required by traditional search.")
            
        with st.expander("2. What information do people actually remember about a photo?"):
            st.write("Users retain contextual and visual anchors. The most common retained memories are visual characteristics (10.4%), co-occurring people/faces (10.2%), and emotional significance (8.2%). They remember *what* the photo felt like or looked like, not *when* it was taken.")
            
        with st.expander("3. What information have they forgotten (or what metadata broke down)?"):
            st.write("The primary failure point is **chronological metadata (23.5%)**. Users forget exact dates, or EXIF data is stripped during external backups and downloads. Because the primary gallery is optimized for a timeline scroll, this missing chronological anchor completely breaks the retrieval loop.")
            
        with st.expander("4. How do users formulate searches when their memory is incomplete?"):
            st.write("Users attempt vague, descriptive keyword searches based on sentiment or physical context. Because current search architectures expect rigid entity nouns, these descriptive queries fail.")
            
        with st.expander("5. What are the most common fallback behaviors when search fails?"):
            st.write("The dominant fallback is **manual timeline grid scrubbing (13.5%)**, followed by desperate, multi-keyword guessing (8.4%). Both are highly repetitive, high-effort actions that rapidly exhaust the user.")
            
        with st.expander("6. What is the business cost of these retrieval failures?"):
            st.write("The friction is severe. **84.2% of all classified retrieval issues are marked as High Severity**. When users hit a memory dead-end and are forced to scrub the grid manually, it leads to direct complaints and explicit threats to abandon the platform.")
            
        with st.expander("7. Is this friction isolated to a specific operating system or cohort?"):
            st.write("No. While our primary data volume came from Android users (87.5%), severe episodic retrieval failures are structurally identical across the Apple App Store and Reddit communities. It is a universal human memory problem, not a localized OS bug.")
            
        with st.expander("8. What is the strategic opportunity area?"):
            st.write("Building an **Episodic AI Anchor**. Instead of trying to repair broken EXIF metadata, the highest impact opportunity is building a conversational interface that successfully parses vague, context-heavy memory prompts.")

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
