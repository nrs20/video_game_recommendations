from flask import Flask, render_template, request
import random
import pandas as pd
import numpy as np

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

@app.route("/recommend", methods=["POST"])
def recommend_games():
    genre = request.form.get("genre")
    user_score_threshold = float(request.form.get("user_score"))

    # Implement your recommendation logic based on user input
    recommended_games = [
        game for game in games
        if genre.lower() in [genre.lower() for genre in game["Genre"]]
        and not np.isnan(game["User_Score"])
        and game["User_Score"] >= user_score_threshold
    ]

    # Shuffle the recommended games list and choose 15 random games
    random.shuffle(recommended_games)
    recommended_games = recommended_games[:15]

    print(recommended_games)  # Add this line to check the content of recommended_games

    return render_template("recommendations.html", games=recommended_games)

if __name__ == "__main__":
    app.run(debug=True)
