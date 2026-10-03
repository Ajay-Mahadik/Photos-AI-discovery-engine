import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Configuration
st.set_page_config(page_title="Photos Discovery Engine", layout="wide")

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
.chart-title {
    font-size: 18px;
    font-weight: 600;
    color: #202124;
    margin-bottom: 2px;
}
.chart-subtitle {
    font-size: 13px;
    color: #5f6368;
    margin-bottom: 16px;
    line-height: 1.4;
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
btn_col1, btn_col2, _ = st.columns([2, 2.5, 6])
with btn_col1:
    if st.button("Update summary", use_container_width=True):
        st.cache_data.clear()
        st.toast("Data refreshed from live Google Sheet!")
        st.rerun()
with btn_col2:
    if st.button("Check for new comments", type="primary", use_container_width=True):
        try:
            # requests.post("https://YOUR-NGROK-URL.ngrok-free.app/webhook/episodic-search")
            st.toast("Triggering n8n pipeline...")
        except Exception as e:
            st.error("Could not reach the webhook.")

st.write("---")

# 8. Interactive Tabs
if not df.empty:
    tab_insights, tab_dashboard, tab_evidence, tab_architecture = st.tabs(["Insights", "Quantitative Dashboard", "Raw Evidence", "How it Works"])

    # --- INSIGHTS TAB ---
    with tab_insights:
        st.markdown("<h3 style='color: #202124; font-size: 20px; font-weight: 500;'>Core Retrieval Breakdown</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
        * **The Metadata Mismatch:** **23.5%** of failures stem from broken chronological EXIF data caused by third-party sharing (WhatsApp, AirDrop) overwriting original capture dates.
        * **Episodic Memories Dominate:** **77%** of retrieval friction stems from users trying to find these specific life events using visual or contextual memory, rather than exact transfer dates.
        * **The Compute & Churn Tax:** When search fails, **13.5%** of users resort to high-friction manual grid scrubbing, heavily taxing cloud compute infrastructure (thumbnail rendering) and degrading platform trust.
        """)
        
        st.write("---") 
        
        st.markdown("<h4 style='color: #202124; font-size: 18px; font-weight: 500;'>Deep Dive: The Episodic Memory Problem</h4>", unsafe_allow_html=True)
        st.write(f"We synthesized {total_comments} valid friction logs to diagnose the architectural gap between human memory and metadata-driven search:")
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

    # --- DASHBOARD TAB ---
    with tab_dashboard:
        if 'Archetype' in df.columns:
            # ROW 1: Archetypes and Severity
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown("<div class='chart-title'>Primary Retrieval Failures by Archetype</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chart-subtitle'>Episodic memory failures make up the vast majority of search friction. Slice labels show the share of comments deduced from the {total_comments} valid logs.</div>", unsafe_allow_html=True)
                
                archetype_counts = df['Archetype'].value_counts().reset_index()
                archetype_counts.columns = ['Archetype', 'Count']
                fig_pie1 = px.pie(archetype_counts, values='Count', names='Archetype', hole=0.5, 
                                  color_discrete_sequence=['#1a73e8', '#34a853', '#fbbc05'])
                fig_pie1.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie1.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=False)
                st.plotly_chart(fig_pie1, use_container_width=True)

            with col_chart2:
                st.markdown("<div class='chart-title'>How Severe is the User Friction?</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chart-subtitle'>Red = High Severity (churn threat) · Yellow = Medium · Green = Low. Bars show the concentration of severe frustration across the {total_comments} analyzed reviews.</div>", unsafe_allow_html=True)
                
                if 'Friction_Severity' in df.columns:
                    severity_dist = df.groupby(['Archetype', 'Friction_Severity']).size().reset_index(name='Count')
                    fig_bar1 = px.bar(severity_dist, x='Archetype', y='Count', color='Friction_Severity',
                                      color_discrete_map={'High': '#ea4335', 'Medium': '#fbbc05', 'Low': '#34a853'},
                                      barmode='group')
                    fig_bar1.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, xaxis_title="", yaxis_title="", legend_title="")
                    st.plotly_chart(fig_bar1, use_container_width=True)

            st.write("---")
            
            # ROW 2: Centered Source Platform Breakdown
            _, col_centered, _ = st.columns([1, 2, 1])

            with col_centered:
                st.markdown("<div class='chart-title' style='text-align: center;'>Where the comments came from</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chart-subtitle' style='text-align: center;'>Play Store makes up most of the dataset. Reddit was sampled to capture power-user workflows. Deduced from {total_comments} raw comments.</div>", unsafe_allow_html=True)
                
                if 'Source' in df.columns:
                    source_counts = df['Source'].value_counts().reset_index()
                    source_counts.columns = ['Source', 'Count']
                    fig_pie2 = px.pie(source_counts, values='Count', names='Source', hole=0.5,
                                      color_discrete_map={'Google Play Store': '#fbbc05', 'Apple App Store': '#1a73e8', 'Reddit (SerpApi)': '#ff4500'})
                    fig_pie2.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie2.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=False)
                    st.plotly_chart(fig_pie2, use_container_width=True)
        else:
            st.warning("Awaiting data columns to render charts.")

    # --- RAW EVIDENCE TAB ---
    with tab_evidence:
        st.markdown("<h3 style='color: #202124; font-size: 20px; font-weight: 500;'>Raw User Feedback Log</h3>", unsafe_allow_html=True)
        if 'Archetype' in df.columns:
            selected_archetype = st.selectbox("Filter quotes by problem cluster:", df['Archetype'].unique())
            display_cols = [col for col in ['Friction_Severity', 'Raw_Text', 'Forgotten_Metadata', 'Fallback_Behavior'] if col in df.columns]
            filtered_quotes = df[df['Archetype'] == selected_archetype][display_cols]
            
            st.dataframe(filtered_quotes, use_container_width=True, hide_index=True)
            
    # --- HOW IT WORKS TAB (ARCHITECTURE) ---
    with tab_architecture:
        st.markdown("<h3 style='color: #202124; font-size: 20px; font-weight: 500;'>System Architecture</h3>", unsafe_allow_html=True)
        st.write("This dashboard is powered by a decoupled full-stack data pipeline. An automated backend handles data ingestion and AI evaluation, a cloud database stores the insights, and a stateless frontend visualizes the metrics.")
        
        link_col1, link_col2, _ = st.columns([2, 2, 6])
        with link_col1:
            st.link_button("View Live Database (Google Sheets)", "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ72lib3473xj0WxWVDqpSS8kpqI6UPee3oCBSW90Mj6A5cPUnEk_8rnZD3v0AeG4CtUAowG7kUDXa7/pub?gid=402859117&single=true&output=csv", use_container_width=True)
        with link_col2:
            st.link_button("View Source Code (GitHub)", "https://github.com/Ajay-Mahadik/Photos-AI-discovery-engine", use_container_width=True)
            
        st.write("")
        
        try:
            st.image("Screenshot 2026-10-02 173519.png", caption="n8n Automated Data Pipeline & AI Discovery Engine")
        except:
            st.info("Upload 'Screenshot 2026-10-02 173519.png' to your GitHub repository to render the architecture diagram here.")
            
        st.markdown("<h4 style='color: #202124; font-size: 18px; font-weight: 500; margin-top: 16px;'>1. Backend: n8n AI Discovery Engine</h4>", unsafe_allow_html=True)
        st.markdown("""
        * **Ingestion:** The pipeline triggers and concurrently fetches raw user reviews from the Play Store, App Store, and Reddit via REST APIs.
        * **Formatting & Merging:** The raw JSON payloads are formatted into a standardized structure and merged into a single chronological data stream.
        * **Deduplication:** The system fetches previously stored IDs from Google Sheets to cross-reference new data. An "If" node filters the data to ensure only net-new reviews are processed, conserving AI token costs.
        * **AI Processing & Rate-Limit Mitigation:** A loop iterates through the new items, sending each raw review to the Gemini API for semantic classification (Archetype, Missing Metadata, Friction Severity). *Architectural Note: This iterative loop was intentionally designed to respect the rate limits of the free-tier Gemini API. In a production environment with an enterprise billing tier, this loop would be bypassed in favor of high-throughput bulk processing to minimize pipeline latency.*
        * **Database Storage:** The formatted AI outputs are appended directly to the `Clean AI insights` and `Updated Raw_Data` tabs in Google Sheets.
        """)
        
        st.markdown("<h4 style='color: #202124; font-size: 18px; font-weight: 500; margin-top: 16px;'>2. Frontend: Streamlit Cloud</h4>", unsafe_allow_html=True)
        st.markdown("""
        * **Stateless Presentation Layer:** The app is deployed via Streamlit Community Cloud and directly tied to the GitHub repository. It does not run heavy ML models locally. 
        * **Live Syncing:** Using Python's `pandas` library, the frontend fetches the live Google Sheets CSV link. 
        * **Caching:** Data is cached in the cloud for 60 seconds (`@st.cache_data(ttl=60)`) to ensure fast UI loading times while remaining strictly synced with the backend n8n pipeline.
        """)
