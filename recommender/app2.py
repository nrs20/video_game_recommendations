from flask import Flask, render_template, request, Markup, redirect, url_for, flash, session
import random
import pandas as pd
import numpy as np
import requests
import re
import urllib.parse 
from bs4 import BeautifulSoup
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
app = Flask(__name__)

# Preprocessed game data
df = pd.read_csv('Video_Games.csv')

# Define the columns we want to keep for the recommendation
relevant_columns = ['Name', 'Genre', 'Platform', 'User_Score']

# Filter the DataFrame to keep only the relevant columns
df = df[relevant_columns]

# Convert the DataFrame to a list of dictionaries
games = df.to_dict(orient='records')

# Convert genres and platforms from strings to lists
for game in games:
    game['Genre'] = game['Genre'].split(',') if isinstance(game['Genre'], str) else []
    game['Platform'] = game['Platform'].split(',') if isinstance(game['Platform'], str) else []

    # Convert 'tbd' to NaN for User_Score
    if game['User_Score'] == 'tbd':
        game['User_Score'] = np.nan
    else:
        game['User_Score'] = float(game['User_Score'])

@app.route("/")
def index():
    return render_template("index.html")
def fetch_game_description(title):
    # Replace YOUR_API_KEY with your actual API key from RAWG (sign up to get the API key)
    api_key = "33b676f49ef74f21860f648158668b42"
    formatted_title = title.replace(" ", "-").replace(":", "").replace("'", "").replace(".", "").lower()

    # Remove consecutive hyphens (replace them with a single hyphen)
    formatted_title = formatted_title.replace("--", "-")    
    url = f"https://api.rawg.io/api/games/{formatted_title.lower()}?key={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        game_data = response.json()

        # Get the description from the API response
        description = game_data.get("description", "Description not available.")
        if description == "Description not available.":
            # If description is not available, create a Google search link
            google_search_link = f"https://www.google.com/search?q={urllib.parse.quote(title)}"
            return Markup(f"Description not available. <a href='{google_search_link}' target='_blank'>Search on Google</a>.")
        else:
  # Use BeautifulSoup to remove HTML elements and convert HTML entities
            soup = BeautifulSoup(description, "html.parser")
            clean_description = soup.get_text()
        # Remove HTML tags from the description using regular expression
            clean_description = re.sub('<[^<]+?>', '', description)

        # Split the description into sentences and take the first two sentences
            sentences = clean_description.split('. ')
            if len(sentences) >= 2:
                clean_description = '. '.join(sentences[:2])

            return clean_description
    except requests.exceptions.RequestException as e:
        print(f"Error fetching description for {title}: {e}")
        return "Error fetching description."
@app.route("/recommend", methods=["POST"])
def recommend_games():
    genre = request.form.get("genre")
    platform = request.form.get("platform")
    user_score_threshold = float(request.form.get("user_score"))

    # Implement your recommendation logic based on user input
    recommended_games = [
        game for game in games
        if genre.lower() in [genre.lower() for genre in game["Genre"]]
        and game["Platform"] and platform.lower() in [platform.lower() for platform in game["Platform"]]
        and not np.isnan(game["User_Score"])
        and game["User_Score"] >= user_score_threshold
    ]

    # Fetch descriptions for each game using the RAWG API
    for game in recommended_games:
        title = game['Name']
        game['Description'] = fetch_game_description(title)

    # Shuffle the recommended games list and choose 15 random games
    random.shuffle(recommended_games)
    recommended_games = recommended_games[:5]

    print(recommended_games)  # Add this line to check the content of recommended_games

    return render_template("recommendations.html", games=recommended_games)


if __name__ == "__main__":
    app.run(debug=True)
