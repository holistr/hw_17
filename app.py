import movies as movies
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

import utils
from models import Movie, Director, Genre
from schemas import movie_schema, movies_schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route("/")
class MoviesView(Resource):

    def get(self):
        movie_with_genre_and_director = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating,
                                                         Movie.trailer,
                                                         Genre.name.label('genre'),
                                                         Director.name.label('director')).join(Genre).join(Director)

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.director_id == director_id)
        if genre_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.genre_id == genre_id)

        movies_list = movie_with_genre_and_director.all()

        return movie_with_genre_and_director(movies_list), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый объект с id {new_movie.id} создан!", 201


@movie_ns.route("/<int:movie_id>")
class MovieView(Resource):

    def get(self, movie_id: int):
        movie = db.session.query(Movie).get(movie_id)
        if movie:
            return movie_schema.dump(movie)
        return "Нет такого фильма", 404

    def patch(self, movie_id: int):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404

        req_json = request.json
        if 'title' in req_json:
            movie.title = req_json['title']
        elif 'description' in req_json:
            movie.description = req_json['description']
        elif 'trailer' in req_json:
            movie.trailer = req_json['trailer']
        elif 'rating' in req_json:
            movie.rating = req_json['rating']
        elif 'year' in req_json:
            movie.year = req_json['year']
        elif 'genre_id' in req_json:
            movie.genre_id = req_json['genre_id']
        elif 'director_id' in req_json:
            movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Объект с id {movie_id} обновлен!", 204

    def put(self, movie_id):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404

        req_json = request.json
        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.year = req_json['year']
        movie.trailer = req_json['trailer']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Объект с {movie_id} обновлен", 204

    def delete(self, movie_id):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404

        db.session.delete(movie)
        db.session.commit()
        return f"Объект с {movie_id} удален ", 204


movies = utils.pagination(movies, utils.page, utils.page_size).all()
page = int(request.args.get('page', 1))
page_size = int(request.args.get('page_size', 10))

if __name__ == '__main__':
    app.run(debug=True)
