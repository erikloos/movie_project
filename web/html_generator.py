from movie_storage import movie_storage_sql as storage


def serialize_movie_grid(user_name: str) -> str:
    """Serialize movies into HTML-text."""
    movies = storage.list_movies(user_name)

    movie_output = ""
    for movie_title, movie_data in movies.items():
        imdb_id = movie_data.get("imdb_id")
        imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"

        note = movie_data.get("note") or "No note yet"
        poster_url = movie_data.get("poster_url") or "https://placehold.co/128x193"

        movie_output += '<li>\n'
        movie_output += '<div class="movie">\n'
        movie_output += f'<a href="{imdb_link}" target="_blank">\n'
        movie_output += f'<img class="movie-poster" src="{poster_url}" title="{note}">\n'
        movie_output += '</a>\n'
        movie_output += f'<div class="movie-title">{movie_title}</div>\n'
        movie_output += f'<div class="movie-year">{movie_data.get("year")}</div>\n'
        movie_output += (f'<div class="movie-imdb-rating">IMDb:'
                         f' {movie_data.get("imdb_rating")}</div>\n')
        movie_output += '</div>\n'
        movie_output += '</li>\n'
    return movie_output


def get_html_template(file_path: str) -> str:
    """Loads HTML file"""
    with open(file_path, "r", encoding="utf-8") as html_file:
        return html_file.read()


def create_page_with_content(new_html_content: str) -> None:
    """Creates an HTML File with the content."""
    with open("_static/index.html", "w", encoding="utf-8") as file:
        file.write(new_html_content)


def generate_website(user_name: str) -> None:
    """Generate a movie website for the current user."""
    html_content = get_html_template("_static/index_template.html")
    movie_grid_html = serialize_movie_grid(user_name)
    new_html_content = html_content.replace("__TEMPLATE_TITLE__", f"{user_name}'s Movie App")
    new_movie_grid_html = new_html_content.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)
    create_page_with_content(new_movie_grid_html)
    print("Website was generated successfully.")