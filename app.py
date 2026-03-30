"""
Flask web application for managing users and their movie collections.

Uses OMDb API to fetch movie details and SQLAlchemy for persistence.
"""


from flask import Flask, request, redirect, url_for, render_template, jsonify
from models import db, User, Movie
from data_manager import DataManager
import os
import requests
from dotenv import load_dotenv



# Resolve the absolute path of the directory containing this file,
# used to build a reliable path for the SQLite database.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Bind the SQLAlchemy instance to this Flask app
db.init_app(app)

# Create all database tables if they don't already exist
with app.app_context():
    db.create_all()


data_manager = DataManager()

@app.route('/')
def index():
    """Render the home page with a list of all users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)




@app.route('/users')
def list_users():
    """Render the full user list (same template as the index)."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)  # Temporarily returning users as a string


@app.route('/users', methods=['POST'])
def add_user():
    """
    Create a new user from form data and redirect to the index.

    Returns:
        400 if the username is empty.
        409 if a user with that name already exists.
    """
    new_user = request.form.get('new_user')
    if not new_user:
        return "Username cannot be empty", 400
    existing = User.query.filter_by(name=new_user).first()
    if existing:
        return "User already exists", 409
    data_manager.create_user(new_user)
    return redirect(url_for('index'))




@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    """
    Display all movies belonging to the given user.

    Args:
        user_id: Primary key of the user whose movies to show.

    Returns:
        A rendered movies page, or a 404 page if the user doesn't exist.
    """
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return render_template('404.html'), 404

    chosen_user_movies = Movie.query.filter(Movie.user_id == user_id).all()
    return render_template('movies.html', movies=chosen_user_movies, user=user)





@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """
    Look up a movie via the OMDb API and add it to the user's collection.

    Reads the movie title from the submitted form, queries OMDb for
    metadata (year, director, poster), and persists the result.

    Args:
        user_id: Primary key of the user to associate the movie with.

    Returns:
        A redirect to the user's movie list on success, or an
        appropriate error message/status code on failure.

    """
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return "User not found", 404
    name = request.form.get('name')
    if not name:
        return "Movie name cannot be empty", 400
    api_key = os.environ.get("APIKEY")
    if not api_key:
        return "API key not configured", 500

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
        return redirect(url_for('get_movies', user_id=user_id))

    except requests.exceptions.ConnectionError:
        print("Error: No internet connection.")
        return None

    # to catch other errors

    except Exception as e:
        print(f"Error: {e}")





@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """
    Update the title of an existing movie.

    Args:
        user_id:  Owner of the movie.
        movie_id: Primary key of the movie to update.

    Returns:
        A redirect to the user's movie list, or 400/404 on error.
    """
    chosen_movie = Movie.query.filter(Movie.user_id == user_id, Movie.id == movie_id).first()
    if not chosen_movie:
        return "Movie not found", 404
    new_title = request.form.get('title')
    if not new_title:
        return "Title cannot be empty", 400
    data_manager.update_movie(movie_id, new_title.strip())
    return redirect(url_for('get_movies', user_id=user_id))




@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """
    Remove a movie from a user's collection.

    Args:
        user_id:  Owner of the movie.
        movie_id: Primary key of the movie to delete.

    Returns:
        A redirect to the user's movie list, or 404 if not found.
    """
    chosen_movie = Movie.query.filter(Movie.user_id == user_id, Movie.id == movie_id).first()
    if not chosen_movie:
        return "Movie not found", 404
    data_manager.delete_movie(movie_id)
    return redirect(url_for('get_movies', user_id=user_id))


# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__=="__main__":
    app.run(host="127.0.0.1", port=5001, debug=True )










