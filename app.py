import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re

def google_search_scrape(query, days_limit=10, max_results=30):
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

        # Extract date (if mentioned in snippet)
        date_match = re.search(r'(\d+\s+days? ago)', snippet_text)
        if date_match:
            days_ago = int(date_match.group(1).split()[0])
            if days_ago > days_limit:
                continue
        elif "hour ago" not in snippet_text and "minute ago" not in snippet_text:
            continue

        # Basic filtering
        if any(x in snippet_text.lower() for x in ["hiring", "engineer", "developer", "medical"]):
            results.append({
                "Title": title.get_text() if title else 'N/A',
                "Link": link,
                "Snippet": snippet_text
            })

    return results

# Streamlit UI
st.title("🔍 Live Job Scraper: HealthTech & MedTech Engineering Roles")
st.write("Fetches recent engineering jobs from companies in Medical Equipment, HealthTech, and MedTech sectors.")

query_input = st.text_input("🔎 Enter your job search query:",
                            "site:linkedin.com/in OR site:linkedin.com/jobs (hiring engineer) (medtech OR healthtech)")
days = st.slider("🗓️ Show posts from last X days:", 1, 30, 10)
search_btn = st.button("🚀 Fetch Jobs")

if search_btn:
    with st.spinner("Scraping job posts from Google Search..."):
        scraped_results = google_search_scrape(query_input, days_limit=days)
        if scraped_results:
            df = pd.DataFrame(scraped_results)
            st.success(f"✅ Found {len(df)} job-related posts")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, "job_posts.csv", "text/csv")
        else:
            st.warning("No relevant results found. Try adjusting your query or timeframe.")
