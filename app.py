from flask import Flask, request, redirect, url_for, render_template, jsonify
from models import db, User, Movie
from data_manager import DataManager
import os
import requests
from dotenv import load_dotenv



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


data_manager = DataManager()

@app.route('/')
def index():
    users = data_manager.get_users()
    return render_template('index.html', users=users)




@app.route('/users')
def list_users():
    users = data_manager.get_users()
    return render_template('index.html', users=users)  # Temporarily returning users as a string


@app.route('/users', methods=['POST'])
def add_user():
    new_user = request.form.get('new_user')
    data_manager.create_user(new_user)
    return redirect(url_for('home'))



@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    chosen_user_movies = Movie.query.filter(Movie.user_id == user_id).all()
    return jsonify([{
      "id": m.id,
      "name": m.name,
      "director": m.director,
      "year": m.year,
      "poster_url": m.poster_url
  } for m in chosen_user_movies])




@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    name = request.form.get('name')
    api_key = os.environ.get("APIKEY")

    try:
        # Make a GET request to the OMDb API using the provided movie title
        movie_data = requests.get(f"https://www.omdbapi.com/?apikey={api_key}&t={name}")
        json_movie_data = movie_data.json()
        # OMDb returns this specific payload when no match is found
        if json_movie_data == {'Response': 'False', 'Error': 'Movie not found!'}:
            return f"The movie {name} not found"

        # Extract the relevant fields from the JSON response
        name = json_movie_data["Title"]
        year = json_movie_data["Year"]
        poster_url = json_movie_data["Poster"]
        director = json_movie_data["Director"]
        data_manager.create_movie(name, director,year, poster_url, user_id)
        return "done"

    except requests.exceptions.ConnectionError:
        print("Error: No internet connection.")
        return None

    # to catch other errors

    except Exception as e:
        print(f"Error: {e}")





@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    chosen_movie = Movie.query.filter(Movie.user_id ==user_id, Movie.id == movie_id).first()
    if chosen_movie:
        new_title = request.form.get('new_title')
        data_manager.update_movie(movie_id, new_title)
    return str(chosen_movie)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    chosen_movie = Movie.query.filter(Movie.user_id == user_id, Movie.id == movie_id).first()
    if chosen_movie:
        data_manager.delete_movie(movie_id)
    return str(chosen_movie)


if __name__=="__main__":
    app.run(host="127.0.0.1", port=5001, debug=True )










