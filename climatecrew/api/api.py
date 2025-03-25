from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure OpenAI
openai.api_key = OPENAI_API_KEY


@app.route('/api/climate-news', methods=['GET'])
def get_climate_news():
    """
    Endpoint to fetch and summarize climate news
    Query parameters:
    - count: number of news items (default 10)
    - days: how many days back to fetch news (default 3)
    """
    try:
        # Get query parameters
        count = int(request.args.get('count', 10))
        days_back = int(request.args.get('days', 3))

        # Fetch news
        news_data = fetch_climate_news(NEWS_API_KEY, days_back, count)

        if not news_data or 'articles' not in news_data:
            return jsonify({"error": "Failed to fetch news articles"}), 500

        # Process and summarize articles
        processed_news = process_news_articles(news_data['articles'])

        return jsonify({"news": processed_news})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def fetch_climate_news(api_key, days_back=3, page_size=10):
    """
    Fetch climate-related news from NewsAPI
    """
    # Calculate date for news not older than days_back
    from_date = (datetime.now() - timedelta(days=days_back)
                 ).strftime('%Y-%m-%d')

    # Build the API URL
    base_url = "https://newsapi.org/v2/everything"

    # Parameters for the API request
    params = {
        'q': 'climate change OR global warming OR renewable energy OR sustainability',
        'language': 'en',
        'from': from_date,
        'sortBy': 'publishedAt',
        'apiKey': api_key,
        'pageSize': page_size
    }

    # Make the request
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching news: {response.status_code}")
        return None


def summarize_with_llm(title, content):
    """
    Summarize the news article using OpenAI's GPT model
    """
    prompt = f"""
    Please summarize the following news article in a concise, engaging way (around 60-80 words):
    
    Title: {title}
    
    Content: {content}
    
    Provide only the summary, without any introduction or explanation.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled news editor who creates concise summaries of climate news."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error summarizing content: {e}")
        return "Summary unavailable"


def process_news_articles(articles):
    """
    Process each news article and create summaries
    """
    processed_news = []

    for article in articles:
        # Skip articles with missing information
        if not article.get('title') or not article.get('description') or not article.get('url'):
            continue

        title = article['title']
        content = article['description']
        if article.get('content'):
            content += " " + article['content']
        source_url = article['url']

        # Get summary from LLM
        summary = summarize_with_llm(title, content)

        # Create processed article
        processed_article = {
            "title": title,
            "content": summary,
            "source_url": source_url,
            "published_at": article.get('publishedAt'),
            "source_name": article.get('source', {}).get('name', 'Unknown'),
            "image_url": article.get('urlToImage')
        }

        processed_news.append(processed_article)

    return processed_news

# Add other routes and endpoints here


if __name__ == "__main__":
    app.run(debug=True)
