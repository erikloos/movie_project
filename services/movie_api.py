import os
from dotenv import load_dotenv
import requests

load_dotenv()
API = os.getenv('API')
API_KEY = os.getenv('API_KEY')


def validate_and_parse_api_response(
        movie_info: dict[str, str]
    ) -> dict[str, str | int | float | None] | None:
    """Validates the response object and return the extracted movie data."""
    if movie_info.get("Response") != "True":
        return None

    title = movie_info.get("Title")
    if not title:
        return None

    try:
        imdb_rating = float(movie_info.get("imdbRating"))
    except (ValueError, TypeError):
        return None

    try:
        year = int(movie_info.get("Year"))
    except (ValueError, TypeError):
        return None

    poster_url = movie_info.get("Poster")

    if poster_url:
        poster_url = poster_url.strip()

    if not poster_url or poster_url == "N/A":
        poster_url = None

    imdb_id = movie_info.get("imdbID")

    return {
        "title": title,
        "year": year,
        "imdb_rating": imdb_rating,
        "poster_url": poster_url,
        "imdb_id": imdb_id
    }


def make_api_response(params: dict[str, str]) -> requests.Response | None:
    """Gets parameters for the API request and returns a response object if successful."""
    try:
        response = requests.get(API, params=params, timeout=5)
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException:
        return None
    return response


def get_search_api_response(search_title: str) -> requests.Response | None:
    """Send a movie request by search to the API and return a response object if successful."""
    params = {"apikey": API_KEY, "s": search_title, "type": "movie"}
    return make_api_response(params)


def get_movie_api_response(imdb_id: str) -> requests.Response | None:
    """Send a movie request by ID to the API and return a response object if successful."""
    params = {"apikey": API_KEY, "i": imdb_id}
    return make_api_response(params)


def get_movie_data_by_id(imdb_id: str) -> tuple[dict[str, str | int | float | None] | None, str | None]:
    """Fetch and validate movie data from API by imdb_id"""
    movie_response = get_movie_api_response(imdb_id)

    if movie_response is None:
        return None, "api_error"

    if movie_response.status_code != 200:
        return None, "api_error"

    try:
        movie_info = movie_response.json()
    except ValueError:
        return None, "invalid_json"

    movie_data = validate_and_parse_api_response(movie_info)

    if movie_data is None:
        return None, "invalid_data"

    return movie_data, None


def search_movies_in_api(search_title: str) -> tuple[list[dict[str, str]] | None, str | None]:
    response = get_search_api_response(search_title)
    if response is None:
        return None, "api_error"

    try:
        movie_info = response.json()
    except ValueError:
        return None, "invalid_json"

    if movie_info.get("Response") != "True":
        return None, "not_found"

    return movie_info["Search"], None