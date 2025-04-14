from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
from flask_cors import CORS
import json
import groq  # You'll need to install this: pip install groq
import sqlite3

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure OpenAI (fallback)
openai.api_key = OPENAI_API_KEY

# Configure Groq client
groq_client = groq.Client(api_key=GROQ_API_KEY)


@app.route('/api/generate-task', methods=['GET'])
def generate_task():
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400

        # Connect to the database to get user profile data
        db_path = "../user_auth.db"  # Adjust path as needed
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get user profile information
        cursor.execute('''
            SELECT full_name, city, country, occupation 
            FROM user_profiles 
            WHERE user_id = ?
        ''', (user_id,))

        profile = cursor.fetchone()
        conn.close()

        if not profile:
            return jsonify({"error": "User profile not found"}), 404

        full_name, city, country, occupation = profile
        location = f"{city}, {country}" if city and country else city or country or "unknown location"

        # Generate task using Groq
        task = generate_environmental_task(full_name, location, occupation)

        # Calculate impact points (could be more dynamic based on task difficulty)
        impact_points = 20

        return jsonify({
            "status": "success",
            "task": task,
            "impact_points": impact_points
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_environmental_task(name, location, occupation):
    try:
        # Create prompt for Groq
        prompt = f"""
        Generate a personalized environmental task for {name or 'a user'} who lives in {location} 
        and works as {occupation or 'a professional'}. 
        
        The task should:
        1. Be specific and actionable
        2. Be relevant to their location and occupation when possible
        3. Take less than a day to complete
        4. Have a measurable environmental impact
        5. Be engaging and motivating
        
        Return only the task description in 2-3 sentences without any introductory text.
        """

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are an environmental task generator that creates personalized climate action tasks."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )

        task = response.choices[0].message.content.strip()

        # Remove common introductory phrases
        intro_phrases = [
            "Here's a task:",
            "Task:",
            "Your task:",
            "Environmental task:"
        ]

        for phrase in intro_phrases:
            if task.lower().startswith(phrase.lower()):
                task = task[len(phrase):].strip()

        return task
    except Exception as e:
        print(f"Groq task generation error: {str(e)}")
        # Fallback task if AI fails
        return f"Reduce your carbon footprint today by walking or using public transport instead of driving. If you're in {location}, try finding a local recycling center and properly dispose of any electronic waste you have at home."


@app.route('/api/climate-news', methods=['GET'])
def get_climate_news():
    try:
        # Get query parameters
        page_size = request.args.get('pageSize', default=10, type=int)
        page = request.args.get('page', default=1, type=int)

        # Use specific climate-related keywords for better filtering
        climate_keywords = "climate change OR global warming OR climate crisis OR carbon emissions OR climate action OR sustainability OR pollution OR environment OR biodiversity OR floods OR drought OR heatwave OR deforestation OR renewable energy OR climate policy OR climate adaptation OR climate mitigation OR forest fires OR climate change India OR pollution Delhi OR Ganga cleaning"

        # News API request
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': climate_keywords,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': page_size,
            'page': page,
            'apiKey': NEWS_API_KEY
        }

        response = requests.get(url, params=params)
        news_data = response.json()

        if response.status_code != 200:
            return jsonify({"error": f"News API error: {news_data.get('message')}"})

        articles = news_data.get('articles', [])
        climate_articles = []

        for article in articles:
            title = article.get('title')
            image_url = article.get('urlToImage')
            content = article.get('content') or article.get('description')

            if not (title and content):
                continue

            # Summarize using Groq
            summary = summarize_with_groq(title, content)

            climate_articles.append({
                "title": title,
                "image": image_url,
                "summary": summary
            })

        return jsonify({
            "status": "success",
            "count": len(climate_articles),
            "articles": climate_articles
        })

    except Exception as e:
        return jsonify({"error": str(e)})


def summarize_with_groq(title, content):
    try:
        text_to_summarize = f"Title: {title}\n\nContent: {content}"

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes climate news concisely."},
                {"role": "user", "content": f"Summarize this climate news article in 2-3 clear sentences:\n\n{text_to_summarize}"}
            ],
            max_tokens=150
        )

        summary = response.choices[0].message.content.strip()

        # Remove common introductory phrases
        intro_phrases = [
            "Here is a summary of the article in 2-3 clear sentences:",
            "Here is a summary of the article in 2-3 sentences:",
            "Here's a summary of the article:",
            "Here is a summary:",
            "Summary:"
        ]

        for phrase in intro_phrases:
            if summary.lower().startswith(phrase.lower()):
                summary = summary[len(phrase):].strip()

        return summary
    except Exception as e:
        print(f"Groq summarization error: {str(e)}")
        # Fallback to OpenAI if Groq fails
        return summarize_with_openai(title, content)


def summarize_with_openai(title, content):
    try:
        text_to_summarize = f"Title: {title}\n\nContent: {content}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes climate news concisely."},
                {"role": "user", "content": f"Summarize this climate news article in 2-3 clear sentences:\n\n{text_to_summarize}"}
            ],
            max_tokens=150
        )

        summary = response.choices[0].message.content.strip()

        # Remove common introductory phrases
        intro_phrases = [
            "Here is a summary of the article in 2-3 clear sentences:",
            "Here is a summary of the article in 2-3 sentences:",
            "Here's a summary of the article:",
            "Here is a summary:",
            "Summary:"
        ]

        for phrase in intro_phrases:
            if summary.lower().startswith(phrase.lower()):
                summary = summary[len(phrase):].strip()

        return summary
    except Exception as e:
        # If all summarization fails, return truncated content
        return (content[:150] + '...') if len(content) > 150 else content


if __name__ == '__main__':
    app.run(debug=True, port=5000)
