import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re

def google_search_scrape(query, max_results=50):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={max_results}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = []
    for g in soup.find_all('div', class_='tF2Cxc'):
        title = g.find('h3')
        link = g.find('a')['href'] if g.find('a') else ''
        snippet = g.find('div', class_='VwiC3b')
        snippet_text = snippet.get_text() if snippet else ''

        if title and any(x in snippet_text.lower() for x in ["hiring", "engineer", "developer", "medical", "medtech", "healthtech"]):
            results.append({
                "Job Title / Snippet": title.get_text(),
                "Link": link,
                "Preview": snippet_text
            })

    return results

# Streamlit UI
st.title("🔍 Live Job Scraper: HealthTech & MedTech Engineering Roles")
st.write("Fetches recent engineering jobs from companies in Medical Equipment, HealthTech, and MedTech sectors.")

# Pre-filled query (user doesn't need to enter)
query_input = "site:linkedin.com/in OR site:linkedin.com/jobs (hiring engineer) (medtech OR healthtech OR \"medical devices\")"

search_btn = st.button("🚀 Fetch Jobs Now")

if search_btn:
    with st.spinner("Scraping job posts from Google Search..."):
        scraped_results = google_search_scrape(query_input)
        if scraped_results:
            df = pd.DataFrame(scraped_results)
            st.success(f"✅ Found {len(df)} job-related posts")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, "job_posts.csv", "text/csv")
        else:
            st.warning("No relevant results found. Try again later or tweak the script to use a different search method.")
