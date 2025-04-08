import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def job_board_search_scrape(query, max_results=50):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&count={max_results}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = []
    for item in soup.find_all('li', class_='b_algo'):
        title_tag = item.find('h2')
        snippet_tag = item.find('p')
        link_tag = title_tag.find('a') if title_tag else None

        title = title_tag.get_text().strip() if title_tag else ''
        link = link_tag['href'] if link_tag else ''
        snippet = snippet_tag.get_text().strip() if snippet_tag else ''

        if any(k in snippet.lower() for k in ["hiring", "engineer", "developer", "medical", "medtech", "healthtech"]):
            results.append({
                "Job Title / Snippet": title,
                "Link": link,
                "Preview": snippet
            })

    return results

# Streamlit UI
st.title("🔍 Live Job Scraper: MedTech & HealthTech Engineering Roles")
st.write("Fetches recent engineering jobs from job boards and public company websites (excluding LinkedIn).")

# Pre-filled job board search query
query_input = "(hiring engineer) (medtech OR healthtech OR \"medical devices\") site:angel.co OR site:wellfound.com OR site:indeed.com OR site:glassdoor.com"

search_btn = st.button("🚀 Fetch Jobs Now")

if search_btn:
    with st.spinner("Scraping job posts from Bing Search (public job boards)..."):
        scraped_results = job_board_search_scrape(query_input)
        if scraped_results:
            df = pd.DataFrame(scraped_results)
            st.success(f"✅ Found {len(df)} job-related posts")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, "job_posts.csv", "text/csv")
        else:
            st.warning("No relevant results found. Try again later or tweak the query.")
