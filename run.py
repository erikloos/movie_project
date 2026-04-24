"""
Program to manage a movie database

User can add, delete, update and search movies and gets their stats.
Tha data is saved in the users profile in the database.
"""

import random

import matplotlib.pyplot as plt

from movie_storage import movie_storage_sql as storage
from web.html_generator import generate_website
from services.movie_api import (get_movie_data_by_id, search_movies_in_api)



NO_DATABASE_MSG = "No movies in the database"

EXIT_COMMAND = 0
LIST_MOVIE_COMMAND = 1
ADD_MOVIE_COMMAND = 2
DELETE_MOVIE_COMMAND = 3
UPDATE_PERSONAL_RATING_COMMAND = 4
STATS_COMMAND = 5
RANDOM_MOVIE_COMMAND = 6
SEARCH_MOVIE_COMMAND = 7
SORTED_MOVIE_RATING_COMMAND = 8
SORTED_MOVIE_YEAR_COMMAND = 9
HISTOGRAM_COMMAND = 10
GENERATE_WEBSITE_COMMAND = 11
ADD_UPDATE_NOTE_COMMAND = 12
SWITCH_USERS_COMMAND = 13


def get_valid_rating() -> float:
    """Validates the rating input and return a version with one decimal digit."""
    while True:
        try:
            movie_rating = float(input("Enter movie rating (0-10): ").strip())
            if not 0 <= movie_rating <= 10:
                print(f"Your input {movie_rating} is not valid")
                continue
            break
        except ValueError:
            print("Enter a valid rating of 0.0 - 10.0")

    return round(movie_rating, 1)


def select_movie_from_api_search() -> str | None:
    """Searches for similar movies in the API Database.
    User chooses a movie, if there are movies found."""
    search_title = input("Enter the movie title: ").strip()
    if not search_title:
        print("Enter a valid title.")
        return None

    title_matches, error = search_movies_in_api(search_title)

    if title_matches is None:
        if error == "api_error":
            print("API request failed")
        elif error == "invalid_json":
            print("Invalid API response")
        elif error == "not_found":
            print(f"No movies matching '{search_title}' found")
        return None

    if len(title_matches) == 1:
        return title_matches[0]["imdbID"]

    print_api_movie_matches(title_matches)

    return choose_api_movie_from_matches(title_matches)


def choose_api_movie_from_matches(title_matches: list[dict[str, str]]) -> str | None:
    """Let user choose a movie from title matches and return the imdbID."""
    while True:
        try:
            user_choice = int(input("Choose the correct movie: ").strip())
            if user_choice == 0:
                return None
            if 1 <= user_choice <= len(title_matches):
                break
            print(f"Enter a number between 1 and {len(title_matches)}.")
        except ValueError:
            print("Enter a valid number.")
    selected_movie = title_matches[user_choice - 1]
    return selected_movie["imdbID"]


def print_api_movie_matches(title_matches: list[dict[str, str]]) -> None:
    """Print matching movie from API search."""
    print("0: Exit")
    for index, movie_data in enumerate(title_matches, 1):
        print(f"{index}. {movie_data['Title']} ({movie_data['Year']})")


def add_movie(user_name: str) -> None:
    """Search for movies with the API.
    Select a movie if matching movies found.
    Add the movie to the users profile."""
    imdb_id = select_movie_from_api_search()
    if imdb_id is None:
        return

    movie_data, error = get_movie_data_by_id(imdb_id)
    if movie_data is None:
        if error == "api_error":
            print("API request failed")
        elif error == "invalid_json":
            print("Invalid API response")
        elif error == "invalid_data":
            print("Movie data is not complete")
        return

    storage.save_movie(
        user_name,
        movie_data["title"],
        movie_data["year"],
        movie_data["imdb_rating"],
        movie_data["poster_url"],
        movie_data["imdb_id"]
        )


def print_db_movie_matches(title_matches: list[dict[str, str]]) -> None:
    """Print matching movie from DB search."""
    print("0: Exit")
    for index, movie_data in enumerate(title_matches, 1):
        print(f"{index}. {movie_data['title']} ({movie_data['year']})")


def choose_db_movie_matches(title_matches: list[dict[str, str]]) -> str | None:
    """Let user choose a movie from database title matches and return the title."""
    while True:
        try:
            user_choice = int(input("Choose the correct movie: ").strip())
            if user_choice == 0:
                return None
            if 1 <= user_choice <= len(title_matches):
                break
            print(f"Enter a number between 1 and {len(title_matches)}.")
        except ValueError:
            print("Enter a valid number.")

    selected_movie = title_matches[user_choice - 1]
    return selected_movie["title"]


def select_movie_for_search(user_name: str) -> str | None:
    """Searches for similar movies in the users profile.
    User chooses can choose movie, if there are movies found."""

    search_title = input("Enter the movie title: ").strip()
    if not search_title:
        return None

    title_matches = storage.search_movies_for_user(user_name, search_title)
    if not title_matches:
        print(f"No movies with '{search_title}' found")
        return None

    if len(title_matches) == 1:
        movie = title_matches[0]
        return movie["title"]

    print_db_movie_matches(title_matches)
    return choose_db_movie_matches(title_matches)


def list_movies(user_name: str) -> None:
    """Print all movies of the current users profile."""
    movies = storage.list_movies(user_name)
    print(f"{len(movies)} movies in total\n")

    for title, movie_data in movies.items():
        personal_rating = movie_data["personal_rating"]
        if personal_rating is not None:

            print(f"{title} ({movie_data['year']}): {movie_data['imdb_rating']}\n"
                  f"Your personal rating: {personal_rating}")
        else:
            print(f"{title} ({movie_data['year']}): {movie_data['imdb_rating']}\n")


def delete_movie(user_name: str) -> None:
    """Delete a selected movie from the users profile"""
    title = select_movie_for_search(user_name)
    if title is None:
        return

    storage.delete_movie(user_name, title)


def update_personal_rating(user_name: str) -> None:
    """Update the personal rating for a movie in the users profile."""
    title = select_movie_for_search(user_name)
    if title is None:
        return

    personal_rating = get_valid_rating()
    storage.update_personal_rating(user_name, title, personal_rating)


def search_movie(user_name: str) -> None:
    """Search the current users profile for matching movies."""
    search_title = input("Enter movie name: ").strip()
    if not search_title:
        print("Enter a valid title to search")
        return

    title_matches = storage.search_movies_for_user(user_name, search_title)

    if not title_matches:
        print(f"No movies with '{search_title}' were found.")
        return

    print("Search results:")
    for movie in title_matches:
        print(f"{movie['title']} ({movie['year']}): {movie['imdb_rating']}")


def sorted_movies(user_name: str, attribute: str, reverse: bool = True) -> None:
    """Print all movies in database, based on given attribute (rating, year)
    and based on order (newest -> oldest or oldest -> newest).
    """
    movies = storage.list_movies(user_name)
    sorted_list_of_movies = sorted(
        movies.items(),
        key=lambda item: item[1][attribute],
        reverse=reverse)

    for title, movie_data in sorted_list_of_movies:
        print(f"{title} ({movie_data['year']}): {movie_data['imdb_rating']}")


def sorted_by_rating(user_name: str) -> None:
    """Print all movies in database by rating (best -> worst)."""
    sorted_movies(user_name, "imdb_rating", reverse=True)


def sorted_by_year(user_name: str) -> None:
    """Print all movies in database by year, in an order the user decided."""
    while True:
        sort_choice = input("Enter 'n' for newest first or 'o' for oldest first:").strip().lower()
        if sort_choice in ("n", "o"):
            break
        print("Enter 'n' or 'o'")
    reverse = sort_choice == "n"

    sorted_movies(user_name, "year", reverse)


def average_rating(user_name: str) -> None:
    """Calculate and print the average rating of all movies in the database."""
    movies = storage.list_movies(user_name)
    if not movies:
        print(NO_DATABASE_MSG)
        return
    total_rating = sum(info["imdb_rating"] for info in movies.values())
    avg = total_rating / len(movies)
    print(f"Average rating: {avg:.1f}")


def median_rating(user_name: str) -> None:
    """Calculate and print the median rating of all movies in the database."""
    movies = storage.list_movies(user_name)
    if not movies:
        print(NO_DATABASE_MSG)
        return
    rating_list = [info["imdb_rating"] for info in movies.values()]
    sorted_rating_list = sorted(rating_list)
    n = len(sorted_rating_list)
    if n % 2 == 1:
        print(f"Median rating: {sorted_rating_list[n // 2]}")
    else:
        median = (sorted_rating_list[n // 2 - 1] + sorted_rating_list[n // 2]) / 2
        print(f"Median rating: {median:.1f}")


def find_min_or_max_rated_movie(
        min_or_max,
        prompt: str,
        movies: dict[str, dict[str, int | float]]
        ) -> None:
    """Print the movie with the best or worst rating."""
    if not movies:
        print(NO_DATABASE_MSG)
        return
    title = min_or_max(movies, key=lambda key: movies[key]["imdb_rating"])
    movie_data = movies[title]
    print(f"{prompt} movie: {title} ({movie_data['year']}): {movie_data['imdb_rating']}")


def best_movie(user_name: str) -> None:
    """Print the movie with the highest rating."""
    movies = storage.list_movies(user_name)
    find_min_or_max_rated_movie(max, "Best", movies)


def worst_movie(user_name: str) -> None:
    """Print the movie with the lowest rating."""
    movies = storage.list_movies(user_name)
    find_min_or_max_rated_movie(min, "Worst", movies)


def print_stats(user_name: str) -> None:
    """Print all movie statistics for the current user."""
    average_rating(user_name)
    median_rating(user_name)
    best_movie(user_name)
    worst_movie(user_name)


def random_movie(user_name: str) -> None:
    """Print a random movie from all movies in database."""
    movies = storage.list_movies(user_name)
    if not movies:
        print(NO_DATABASE_MSG)
        return
    random_title = random.choice(list(movies.keys()))
    print(f"Your movie for tonight: {random_title}")


def rating_histogram(user_name: str) -> None:
    """Creates and saves a file of a histogram of the movie database."""
    movies = storage.list_movies(user_name)
    if not movies:
        print(NO_DATABASE_MSG)
        return
    ratings = [info["imdb_rating"] for info in movies.values()]
    plt.clf()
    plt.hist(ratings, bins=10)
    plt.xlabel("IMDb-Ratings")
    plt.ylabel("Number of Movies")
    file_type = input("Filetype for histogram (png, pdf, svg, jpeg)? ").lower().strip()
    if file_type not in ("png", "pdf", "svg", "jpeg"):
        print("Invalid file_type. The file will be saved as PNG by default")
        file_type = "png"
    file_title = input("What name you want to give the file?").strip()
    if file_title == "":
        file_title = "movies"

    file_name = f"{file_title}.{file_type}"
    plt.savefig(file_name)
    plt.show()
    print(f"The histogram was saved as {file_name}")


def add_update_note(user_name: str) -> None:
    """Add, update or clear a movie note for the user."""
    title = select_movie_for_search(user_name)
    if title is None:
        return

    new_note = input("Enter the note you want to add to the movie: ").strip()
    if not new_note:
        print("Note will be cleared")
    storage.update_note(user_name, title, new_note)


def create_user() -> str | None:
    """Create a new user profile and return the username if successful."""
    new_user_name = input("Enter your Username: ").strip()
    if not new_user_name:
        print("Invalid input for Username\n")
        return None
    result =  storage.create_user_in_db(new_user_name)
    if result:
        print(f"Welcome {new_user_name}! Your profile was added successfully.\n")
        return new_user_name
    if result is False:
        print(f"Sorry the name {new_user_name} is already taken.\n")
        return None

    return None

def select_user() -> str | None:
    """User can choose an existing profile and return the username"""
    available_users = storage.list_users()
    print("Available users: ")
    for user in available_users:
        print(user)
    print()
    user_name = input("Enter your Username: ").strip()
    user_check = storage.get_user_id_by_name(user_name)
    if user_check is None:
        print(f"User {user_name} was not found.")
        return None
    return user_name


def show_users() -> None:
    """Print all available usernames"""
    user_names = storage.list_users()
    if not user_names:
        print("No users were found \n")
        return
    print("Users: ")
    for user_name in user_names:
        print(user_name)
    print()


def start_screen() -> None:
    """Print the starting screen header."""
    print("********** My Movies App **********")
    print()


def user_menu() -> int | None:
    """Print the user menu and return the selected option."""
    print(
        "User-Menu:\n"
        "0. Exit\n"
        "1. Select User\n"
        "2. Create new User\n"
        "3. Show Users\n"
    )
    while True:
        try:
            user_menu_operation = int(input("Enter Choice (0-3): "))
            if not 0 <= user_menu_operation <= 3:
                print("Enter a number between 0 and 3.\n")
                continue
            return user_menu_operation

        except ValueError:
            print("Enter a valid number.\n")


def menu() -> int | None:
    """Print the menu of the program and expects an input to do an operation."""
    print(
        "Menu:\n"
        "0. Exit\n"
        "1. List movies\n"
        "2. Add movie\n"
        "3. Delete movie\n"
        "4. Add personal rating\n"
        "5. Stats\n"
        "6. Random movie\n"
        "7. Search movie\n"
        "8. Movies sorted by rating\n"
        "9. Movies sorted by year\n"
        "10. Create an histogram of ratings\n"
        "11. Generate Website\n"
        "12. Add/Update Note\n"
        "13. Log Out\n"
    )
    while True:
        try:
            menu_operation = int(input("Enter Choice (0-13): "))
            if not 0 <= menu_operation <= 13:
                print("Enter a number between 0 and 13.\n")
                continue
            return menu_operation

        except ValueError:
            print("Enter a valid number.\n")


def main() -> None:
    """Run the movie app and handle the main program flow."""
    start_screen()

    command_map = {
        LIST_MOVIE_COMMAND: list_movies,
        ADD_MOVIE_COMMAND: add_movie,
        DELETE_MOVIE_COMMAND: delete_movie,
        UPDATE_PERSONAL_RATING_COMMAND: update_personal_rating,
        STATS_COMMAND: print_stats,
        RANDOM_MOVIE_COMMAND: random_movie,
        SEARCH_MOVIE_COMMAND: search_movie,
        SORTED_MOVIE_RATING_COMMAND: sorted_by_rating,
        SORTED_MOVIE_YEAR_COMMAND: sorted_by_year,
        HISTOGRAM_COMMAND: rating_histogram,
        GENERATE_WEBSITE_COMMAND: generate_website,
        ADD_UPDATE_NOTE_COMMAND: add_update_note
    }
    current_user = None

    while True:
        if current_user is None:
            user_menu_operation = user_menu()
            if user_menu_operation == 0:
                print("Bye!")
                break
            if user_menu_operation == 1:
                selected_user = select_user()
                if selected_user is not None:
                    current_user = selected_user
            elif user_menu_operation == 2:
                created_user = create_user()
                if created_user is not None:
                    current_user = created_user
            elif user_menu_operation == 3:
                show_users()

        else:
            menu_operation = menu()

            if menu_operation == EXIT_COMMAND:
                print("Bye!")
                break

            if menu_operation == SWITCH_USERS_COMMAND:
                print(f"{current_user} logged out!")
                current_user = None

            elif menu_operation in command_map:
                command_map[menu_operation](current_user)

            else:
                print("Invalid input\n")

            input("\nPress enter to continue:")
            print()


if __name__ == "__main__":
    main()
