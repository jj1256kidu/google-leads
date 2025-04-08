import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# === CONFIG ===
SEARCH_TERMS = [
    "medical device engineer",
    "medtech software engineer",
    "healthtech embedded engineer",
    "medical AI developer"
]
BLACKLIST = ["sales", "marketing", "hr", "recruiter", "business development", "bd"]
SHEET_NAME = "For Lead Gen Med Tech"
WORKSHEET_NAME = "Engineering Job Leads"
CREDENTIAL_FILE = "credentials.json"


# === Google Sheets Setup ===
@st.cache_resource
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    return sheet

# === Bing Search Scraper for LinkedIn Jobs ===
def scrape_jobs():
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    for term in SEARCH_TERMS:
        query = f"site:linkedin.com/jobs {term}"
        url = f"https://www.bing.com/search?q={requests.utils.quote(query)}"
        st.info(f"🔍 Searching: {term}")
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        links = [a['href'] for a in soup.find_all("a", href=True) if "linkedin.com/jobs/view" in a['href']]
        for link in links:
            title = term.title()
            if not any(bad in title.lower() for bad in BLACKLIST):
                results.append({
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Company": "Unknown",
                    "Title": title,
                    "Location": "N/A",
                    "Link": link,
                    "Source": "LinkedIn via Bing"
                })

    return results


# === Export to Google Sheets ===
def export_to_sheet(data):
    sheet = connect_to_sheet()
    rows = data[["Timestamp", "Company", "Title", "Location", "Link", "Source"]].values.tolist()
    existing = len(sheet.get_all_values())
    sheet.insert_rows(rows, row=existing + 1)
    st.success(f"✅ Exported {len(rows)} leads to Google Sheet!")


# === Streamlit UI ===
st.title("🔍 MedTech Job Lead Scraper")
st.caption("Scrape LinkedIn job posts for Engineering roles in Medical Devices, HealthTech, and MedTech.")

if st.button("🚀 Fetch Latest Job Leads"):
    job_data = scrape_jobs()
    if job_data:
        df = pd.DataFrame(job_data)
        st.dataframe(df, use_container_width=True)

        if st.button("📤 Export to Google Sheet"):
            export_to_sheet(df)
    else:
        st.warning("❌ No job leads found.")
