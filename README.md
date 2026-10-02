# Google Photos: Episodic Discovery Engine | Project

This repository contains the live data dashboard and automated backend pipeline for the **Episodic AI Anchor**—a product concept designed to solve the "Metadata vs. Episodic Memory Mismatch" in Google Photos.

👉 [View the Live Executive Dashboard Here](https://gphotos-discovery-engine-ajay.streamlit.app/)

## 🧠 The Product Problem
Users frequently struggle to retrieve old photos using contextual or emotional memory (e.g., *"that small cafe in Goa"*). Current search architectures rigidly cross-reference keywords with chronological EXIF data. However, when photos are shared via third-party apps (WhatsApp, AirDrop), the original capture date is overwritten by the transfer date. 

This creates a **23.5% chronological failure rate**, forcing users into high-friction manual grid scrubbing that heavily taxes cloud compute infrastructure and degrades platform trust.

## ⚙️ The Solution Architecture
Instead of relying on users to repair metadata, this project proposes a visual semantic clustering engine. To prove the concept and validate user friction, I built a fully automated data synthesis pipeline.

### Tech Stack
* **Frontend:** Streamlit (Python), Pandas, Google Material Design 3 UI.
* **Backend Pipeline:** n8n (Workflow Automation).
* **AI Engine:** Google Gemini API (for semantic classification and severity mapping).
* **Data Ingestion:** SerpApi (scraping Reddit and App Store reviews).
* **Database:** Google Sheets (Live CSV export).

## 📂 Repository Contents
1. `app.py`: The frontend Streamlit application rendering the live Material Design dashboard.
2. `n8n_ai_classification_pipeline.json`: The exported backend workflow. You can import this directly into any n8n instance to see how the Gemini API parses raw user complaints, maps missing memory anchors, and routes the data.
3. `.streamlit/config.toml`: UI configuration enforcing Google's Light Theme design principles.

## 🚀 How the Pipeline Works
1. **Ingestion:** n8n pings SerpApi to pull live user feedback regarding Google Photos retrieval failures.
2. **Deduplication:** Checks incoming IDs against the master database to prevent redundant API calls.
3. **AI Classification:** Gemini evaluates the `Raw_Text` and categorizes it by Archetype (Episodic, Visual, Ephemeral) and Friction Severity.
4. **Live Visualization:** The Streamlit frontend pulls the processed CSV directly from Google Sheets, dynamically recalculating metrics and rendering Material Design charts without manual intervention.
