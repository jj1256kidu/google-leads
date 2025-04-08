import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------ CONFIG ------------------

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"
SEARCH_TERMS = [
    "medical device engineer",
    "medtech software engineer",
    "healthtech embedded engineer",
    "medical AI developer"
]
BLACKLIST = ["sales", "marketing", "hr", "recruiter", "business development", "bd"]

# Google Sheets config
SHEET_NAME = "For Lead Gen Med Tech"
WORKSHEET_NAME = "Engineering Job Leads"
CREDENTIAL_FILE = "credentials.json"

# ------------------ GOOGLE SHEET ------------------

@st.cache_resource
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    return sheet

def export_to_sheet(data):
    sheet = connect_to_sheet()
    rows = data[["Timestamp", "Company", "Title", "Location", "Link", "Source"]].values.tolist()
    existing = len(sheet.get_all_values())
    sheet.insert_rows(rows, row=existing + 1)
    st.success(f"✅ Exported {len(rows)} rows to Google Sheet!")

# ------------------ GOOGLE SEARCH ------------------

def search_google(query, api_key, cx):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items", [])
        results = []
        for item in items:
            title = item.get("title", "N/A")
            link = item.get("link", "")
            snippet = item.get("snippet", "").lower()

            # Filter: Skip blacklisted words
            if any(word in title.lower() for word in BLACKLIST):
                continue

            # Filter: Skip if looks older than ~30 days
            if any(word in snippet for word in ["1 month", "2 months", "30 days"]):
                continue

            results.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Company": "Unknown",
                "Title": title,
                "Location": "N/A",
                "Link": link,
                "Source": "Google Search API"
            })
        return results
    else:
        st.error(f"🔴 Google Search API Error: {response.status_code}")
        return []

# ------------------ STREAMLIT UI ------------------

st.title("🔍 MedTech Job Lead Finder (via Google)")
st.caption("Fetches engineering job listings from LinkedIn using Google Programmable Search API.")

if st.button("🚀 Search Now"):
    all_jobs = []
    for term in SEARCH_TERMS:
        query = f"{term} site:linkedin.com/jobs"
        st.info(f"Searching for: {term}")
        leads = search_google(query, GOOGLE_API_KEY, SEARCH_ENGINE_ID)
        all_jobs.extend(leads)

    if all_jobs:
        df = pd.DataFrame(all_jobs)
        st.dataframe(df, use_container_width=True)

        if st.button("📤 Export to Google Sheet"):
            export_to_sheet(df)
    else:
        st.warning("❌ No recent job posts found.")
