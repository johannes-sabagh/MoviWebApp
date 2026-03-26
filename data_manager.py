from models import db, User, Movie


class DataManager:
    # Define Crud operations as methods
    def create_user(self, name):
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self):
        return User.query().all()

    def create_movie(self, name, director, year, poster_url):
        new_movie = Movie(name=name, director=director,year=year, poster_url=poster_url )
        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def get_movies(self):
        return Movie.query.all()

    def update_movie(self,movie_id, new_title):
        movie_to_update = Movie.query.filter(Movie.movie_id == movie_id)
        movie_to_update.name = new_title
        db.session.commit()
        return movie_to_update

    def delete_movie(self, movie_id):
        movie_to_delete = Movie.query.filter(Movie.movie_id == movie_id)
        db.session.delete(movie_to_delete)
        db.session.commit()
        return movie_to_delete





