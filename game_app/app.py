from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import plotly.express as px

app = Flask(__name__)

games_df = pd.read_csv('games.csv')

@app.route('/')
def index():
    games = games_df.to_dict(orient='records')
    return render_template('index.html', games=games)

@app.route('/game/<int:game_id>')
def game(game_id):
    game = games_df[games_df['id'] == game_id].to_dict(orient='records')[0]
    return render_template('game.html', game=game)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        new_data = pd.read_csv(file_path)
        games_df = pd.concat([games_df, new_data], ignore_index=True)
        games_df.to_csv('games.csv', index=False)
        return jsonify({'success': 'File uploaded and data updated'})

@app.route('/visualizations')
def visualizations():
    release_histogram = px.histogram(games_df, x='year', title='Game Releases by Year')
    release_histogram_html = release_histogram.to_html(full_html=False)

    genre_bar_chart = px.bar(games_df, x='genre', y='global_sales', title='Game Popularity by Genre')
    genre_bar_chart_html = genre_bar_chart.to_html(full_html=False)

    return render_template('visualizations.html', release_histogram=release_histogram_html, genre_bar_chart=genre_bar_chart_html)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    filtered_games = games_df[games_df.apply(lambda row: query.lower() in row['name'].lower(), axis=1)]
    games = filtered_games.to_dict(orient='records')
    return render_template('index.html', games=games)

if __name__ == '__main__':
    app.run(debug=True)