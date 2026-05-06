# ΨHM Alumni Analytics Dashboard 

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com/)

> **Live Demo:** [Link to deployed Streamlit app here shortly]

An end-to-end data engineering pipeline and interactive visualization dashboard built for the Psi Eta Mu (ΨHM) professional fraternity at the University of Illinois Urbana-Champaign. This tool transforms raw, decentralized alumni records into a secure, centralized, and actionable network map.

![Dashboard Preview](__upload_gif/picture_of_dahsboard_demo_here__)
*(Note: Sensitive contact data has been anonymized for public demonstration).*

## Business Value 
Previously, alumni data was scattered and difficult to leverage. This dashboard provides the executive board and active members with:
* **Instant Geographic Insights:** An interactive heatmap to visualize where alumni live and work, making it easier to plan networking events and for members to see the network breadth.
* **Career Mapping:** Automated categorization of job titles to identify which industries our alumni dominate.
* **Targeted Networking:** Robust filtering to instantly find alumni at specific companies or in specific roles to support undergraduate mentorship.

## Architecture & Tech Stack 
This project is built on a custom ETL (Extract, Transform, Load) pipeline to ensure data remains fresh without manual data entry.

* **Frontend Visualization:** `Streamlit`, `Plotly Express`, `WordCloud`
* **Data Processing:** `Pandas`
* **Backend Database:** `Supabase` (PostgreSQL)
* **Pipeline Integration:** `gspread` (Google Sheets API), `SQLAlchemy`

**The Data Workflow:**
1. Executive board members update the alumni information master Google Sheet.
2. The `sync_pipeline.py` script extracts the new updated data and cleans columns.
3. The cleaned data is pushed securely to a live Supabase PostgreSQL database using connection pooling.
4. The Streamlit app queries the database via SQL to render real-time UI updates.

## Security 
To protect alumni data, this repository is strictly sanitized. All database credentials, Google API keys, and connection URIs are managed securely via Environment Variables (`.env`) and Streamlit Secrets (`secrets.toml`) and are intentionally excluded from version control via `.gitignore`. 

---

## Local Setup 
To run this project locally, you must request the environment credentials from the repository owner.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/phm-alumni-dashboard.git](https://github.com/YOUR-USERNAME/phm-alumni-dashboard.git)
   cd phm-alumni-dashboard
2. **Install Dependencies**
   ```bash
    pip install -r requirements.txt
3. **Configure the Data Pipeline:**

  Duplicate .env.example, rename it to .env, and insert the PostgreSQL connection string. Ensure google_secret.json is placed in the root directory.

5. **Configure the Dashboard:**

  Create a .streamlit folder. Inside, create a secrets.toml file and insert the PostgreSQL connection string.

7. **Run the app**
   ```bash
   streamlit run app.py
