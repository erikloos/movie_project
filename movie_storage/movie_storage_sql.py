"""Module to interact with the database"""
from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///_data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=False)


def get_connection():
    """Create and return a database connection."""
    connection = engine.connect()
    connection.execute(text("PRAGMA foreign_keys = ON"))
    return connection

# Create the user table if it does not exist
with get_connection() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
        )
    """))
    connection.commit()

# Create the movies table if it does not exist
with get_connection() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE NOT NULL,
        year INTEGER NOT NULL,
        imdb_rating REAL NOT NULL,
        poster_url TEXT,
        imdb_id TEXT NOT NULL
        )
    """))
    connection.commit()

# Create the users_movie table if it does not exist
with get_connection() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users_movies(
        user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        note TEXT,
        personal_rating REAL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (movie_id) REFERENCES movies(id),
        UNIQUE (user_id, movie_id)
        )
    """))
    connection.commit()


def get_user_id_by_name(user_name: str) -> int|None:
    """Return the user ID for the username."""
    with get_connection() as connection:
        result = connection.execute(text("SELECT id "
                                         "FROM users "
                                         "WHERE users.name = :user_name"),
                                    {"user_name": user_name})
        row = result.fetchone()
        if row is None:
            return None

        return row[0]


def list_movies(user_name: str) -> dict:
    """Return all movies in the users profile."""
    user_id = get_user_id_by_name(user_name)
    if user_id is None:
        print("User was not found")
        return {}
    with get_connection() as connection:
        result = connection.execute(text("SELECT movies.title, movies.year, "
                                         "movies.imdb_rating, movies.poster_url, "
                                         "users_movies.personal_rating, "
                                         "users_movies.note, movies.imdb_id "
                                         "FROM movies "
                                         "JOIN users_movies "
                                         "ON movies.id = users_movies.movie_id "
                                         "WHERE users_movies.user_id = :user_id "),
                                    {"user_id": user_id})
        rows = result.fetchall()

    return {row[0]: {"year": row[1],
                     "imdb_rating": row[2],
                     "poster_url": row[3],
                     "personal_rating": row[4],
                     "note": row[5],
                     "imdb_id": row[6]} for row in rows}


def get_movie_id_by_title(title: str)-> int|None:
    """Return the movie ID for the given movie title."""
    with get_connection() as connection:
        result = connection.execute(text("SELECT id "
                                         "FROM movies "
                                         "WHERE movies.title = :title"),
                                    {"title": title})
        row = result.fetchone()
        if row is None:
            return None

        return row[0]


def user_has_movie_in_db(user_id: int, movie_id: int) -> bool:
    """Check if the user already have the movie in his profile."""
    with get_connection() as connection:
        result = connection.execute(text("SELECT 1 "
                                         "FROM users_movies "
                                         "WHERE user_id = :user_id AND movie_id = :movie_id "
                                         ),
                           {"user_id": user_id, "movie_id": movie_id})
        row = result.fetchone()
        return row is not None


def get_or_create_movie_id(
        title: str, year: int, imdb_rating: float, poster_url: str, imdb_id: str
) -> int|None:
    """Return the movie ID and creates the movie in the database if it not exist already."""
    movie_id = get_movie_id_by_title(title)
    if movie_id is not None:
        return movie_id

    with get_connection() as connection:
        try:
            connection.execute(text(
                "INSERT INTO movies (title, year, imdb_rating, poster_url, imdb_id) "
                "VALUES (:title, :year, :imdb_rating, :poster_url, :imdb_id)"),
                {"title": title, "year": year, "imdb_rating": imdb_rating,
                 "poster_url": poster_url, "imdb_id": imdb_id})
            connection.commit()

        except Exception as e:
            print(f"Error: {e}")
            return None

    movie_id = get_movie_id_by_title(title)
    return movie_id


def save_movie(
        user_name: str,
        title: str,
        year: int,
        imdb_rating: float,
        poster_url: str|None,
        imdb_id: str|None
) -> None:
    """Add a new movie to the user-profile."""
    user_id = get_user_id_by_name(user_name)
    if user_id is None:
        print("User was not found")
        return

    movie_id = get_or_create_movie_id(title, year, imdb_rating, poster_url, imdb_id)

    if movie_id is None:
        print("Movie could not be added.")
        return

    if user_has_movie_in_db(user_id, movie_id):
        print(f"Movie '{title}' is already in your profile.")
        return

    try:
        with get_connection() as connection:
            connection.execute(text("INSERT INTO users_movies (user_id, movie_id)"
                                    " VALUES (:user_id, :movie_id)"),
                               {"user_id": user_id, "movie_id": movie_id})
            connection.commit()
        print(f"Movie '{title}' added successfully.")
    except Exception as e:
        print(f"Error: {e}")


def delete_movie(user_name: str, title: str) -> None:
    """Deletes a movie from the user-profile."""
    user_id = get_user_id_by_name(user_name)
    if user_id is None:
        print("User was not found")
        return

    movie_id = get_movie_id_by_title(title)
    if movie_id is None:
        print("Movie was not found")
        return

    with get_connection() as connection:
        try:
            result = connection.execute(
                text("DELETE FROM users_movies "
                     "WHERE movie_id = :movie_id AND user_id = :user_id"),
                {"movie_id": movie_id, "user_id": user_id})
            connection.commit()
            if result.rowcount == 0:
                print(f"Movie '{title}' was not found in your profile.")
            else:
                print(f"Movie '{title}' was successfully deleted.")

        except Exception as e:
            print(f"Error: {e}")


def update_personal_rating(user_name: str, title: str, personal_rating: float) -> None:
    """Update personal rating of a movie in the user's profile."""
    user_id = get_user_id_by_name(user_name)
    if user_id is None:
        print("User was not found")
        return
    movie_id = get_movie_id_by_title(title)
    if movie_id is None:
        print("Movie was not found")
        return
    with get_connection() as connection:
        try:
            result = connection.execute(
                text("UPDATE users_movies "
                     "SET personal_rating = :personal_rating "
                     "WHERE movie_id = :movie_id AND user_id = :user_id"),
                {"movie_id": movie_id, "personal_rating": personal_rating, "user_id": user_id})
            connection.commit()
            if result.rowcount == 0:
                print(f"The rating of the movie '{title}' was not updated.")
            else:
                print(f"Personal rating for '{title}' was updated to {personal_rating}.")

        except Exception as e:
            print(f"Error: {e}")


def create_user_in_db(user_name: str) -> bool|None:
    """Creates a user profile in the database, if the username is available."""
    user_id = get_user_id_by_name(user_name)
    if user_id is None:
        try:
            with get_connection() as connection:
                connection.execute(text("INSERT INTO users (name) VALUES ( :user_name)"),
                                   {"user_name": user_name})
                connection.commit()
                return True
        except Exception as e:
            print(f"Error: {e}")
            return None
    else:
        return False


def list_users() -> list[str]:
    """Return a sorted list of all usernames"""
    with get_connection() as connection:
        result = connection.execute(text("SELECT name "
                                         "FROM users "
                                         "ORDER BY name"))
        users = result.fetchall()

    return [user[0] for user in users]


def update_note(user_name: str, title: str, note: str) -> None:
    """Update a movie's personal note for the current user."""
    user_id = get_user_id_by_name(user_name)
    if user_id is None:
        print("User was not found")
        return
    movie_id = get_movie_id_by_title(title)
    if movie_id is None:
        print("Movie was not found")
        return
    with get_connection() as connection:
        try:
            result = connection.execute(
                text("UPDATE users_movies "
                     "SET note = :note "
                     "WHERE movie_id = :movie_id AND user_id = :user_id"),
                {"movie_id": movie_id, "note": note, "user_id": user_id})
            connection.commit()
            if result.rowcount == 0:
                print(f"The note for the movie '{title}' was not updated.")

            else:
                if note == "":
                    print(f"The note for the movie '{title}' was cleared.")
                else:
                    print(f"Note for '{title}' was updated.")

        except Exception as e:
            print(f"Error: {e}")


def search_movies_for_user(user_name: str, search_title: str) -> list:
    """Return movies from the users profile where titles matches the search title."""
    user_id = get_user_id_by_name(user_name)
    if user_id is None:
        return []
    with get_connection() as connection:
        result = connection.execute(text("SELECT title, year, imdb_rating "
                                         "FROM movies "
                                         "JOIN users_movies "
                                         "ON movies.id = users_movies.movie_id "
                                         "WHERE users_movies.user_id = :user_id AND "
                                         "LOWER(movies.title) LIKE LOWER(:title) "
                                         "ORDER BY movies.title"),
                                    {"title": f"%{search_title}%", "user_id": user_id})
        rows = result.fetchall()
        movies = []
        for row in rows:
            movies.append({
                "title": row[0],
                 "year": row[1],
                "imdb_rating": row[2]
            })

        return movies
