"""
Module to get, save, add, delete and update movies into
the database in the JSON file.
"""

import json

DATA_FILE = "data.json"

def get_movies() -> dict[str, dict[str, int | float]]:
    """
    Returns a dictionary of dictionaries that
    contains the movies information in the database.
    The function loads the information from the JSON
    file and returns the data.
    """
    try:
        with open(DATA_FILE, "r") as data_file:
            return json.load(data_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_movies(movies: dict[str, dict[str, int | float]]) -> None:
    """
    Gets all your movies as an argument and saves them to the JSON file.
    """
    with open(DATA_FILE, "w") as data_file:
        json.dump(movies, data_file, indent=4)


def add_movie(title: str, rating: float, year: int) -> None:
    """
    Adds a movie to the movies database.
    Loads the information from the JSON file, add the movie,
    and saves it.
    """
    movies = get_movies()
    movies[title] = {"rating": rating, "year": year}
    save_movies(movies)


def delete_movie(title: str) -> None:
    """
    Deletes a movie from the movies database.
    Loads the information from the JSON file, deletes the movie,
    and saves it.
    """
    movies = get_movies()
    del movies[title]

    save_movies(movies)


def update_movie(title: str, rating: float) -> None:
    """
    Updates a movie from the movies database.
    Loads the information from the JSON file, updates the movie,
    and saves it.
    """
    movies = get_movies()
    movies[title]['rating'] = rating
    save_movies(movies)
