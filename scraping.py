import requests
from bs4 import BeautifulSoup
import json
from gpt_integration import generate_content
import time

# Define categories and URLs
categories = {
    "Business": "https://www.moneycontrol.com/news/business/",
    "Markets": "https://www.moneycontrol.com/news/markets/",
    "Mutual Funds": "https://www.moneycontrol.com/news/mutual-funds/"
}

# Define request headers
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# Dictionary to store all scraped headlines and content
all_headlines = {}

# Initialize a counter to track requests
request_counter = 0

# Retry logic with exponential backoff for API requests
def make_request_with_backoff(url, retries=5, delay=2):
    global request_counter
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            request_counter += 1  # Increment the request counter
            if request_counter % 15 == 0:  # Sleep for 40 seconds after every 25 requests
                print("Reached 15 requests. Sleeping for 40 seconds...")
                time.sleep(30)
            return response
        except requests.RequestException as e:
            if attempt < retries - 1:  # If retries are left
                print(f"Retrying ({attempt + 1}/{retries}) due to error: {e}")
                time.sleep(delay)  # Initial delay
                delay *= 2  # Exponential increase in delay
            else:
                print(f"Failed to fetch after {retries} attempts: {e}")
                return None

# Step 1: Scrape Headlines
for category, url in categories.items():
    print(f"Scraping {category}...")
    response = make_request_with_backoff(url)
    if not response:
        print(f"Skipping {category} due to repeated errors.")
        continue  # Skip this category if requests failed

    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = soup.select('h2 a')  # Adjust CSS selector based on site structure

    # Collecting headlines and links
    cat_data = []
    for h in headlines[:10]:  # Limit to 10 headlines per category
        title = h.text.strip()
        link = h.get('href', '#')  # Fallback to '#' if no URL is found
        cat_data.append({"title": title, "url": link})

    if cat_data:
        all_headlines[category] = cat_data  # Add to the main dictionary

# Step 2: Scrape Article Content
for category, articles in all_headlines.items():
    print(f"Fetching article content for {category}...")
    for article in articles:
        url = article["url"]
        response = make_request_with_backoff(url)
        if not response:
            article["article"] = "Error fetching article"
            continue  # Skip this article if requests failed

        article_soup = BeautifulSoup(response.text, 'html.parser')

        # Extract content from all <p> tags
        content_paragraphs = article_soup.find_all('p')  # Get all <p> tags
        raw_content = "\n".join(
            p.text.strip() for p in content_paragraphs if p.text.strip()
        )

        # Process content with the generate_content function
        try:
            cleaned_content = generate_content(raw_content)
            article["article"] = cleaned_content if cleaned_content else "Content not found"
        except Exception as e:
            print(f"Error generating content for article {url}: {e}")
            article["article"] = "Error generating content"

# Step 3: Save to JSON File
filename = "moneycontrol_cleaned_articles.json"
if all_headlines:
    try:
        with open(filename, "w", encoding="utf-8", errors="ignore") as f:
            json.dump(all_headlines, f, indent=4, ensure_ascii=False)
        print(f"\nSaved data to {filename}")
    except IOError as e:
        print(f"Error saving data to file: {e}")
else:
    print("No data to save.")