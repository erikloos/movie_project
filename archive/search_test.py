# import os
# import requests
# from dotenv import load_dotenv
#
# #Link zusatz = ?i=tt3896198
#
# load_dotenv()
# API = os.getenv('API')
# API_KEY = os.getenv('API_KEY')
#
#
# def get_api_response(search_title: str) -> requests.Response | None:
#     """Send a movie request to the API and returns a response object if successful."""
#     params = {"t": search_title}
#     try:
#         response = requests.get(API, params=params, timeout=5)
#     except requests.exceptions.Timeout:
#         print("Timeout for API Request")
#         return None
#     except requests.exceptions.RequestException as e:
#         print(f"API Request failed: {e}")
#         return None
#
#     return response
#
#
# def get_search_api_response(search_title: str) -> requests.Response | None:
#     """Send a movie request to the API and returns a response object if successful."""
#
#     params = {"apikey": API_KEY, "s": search_title, "type": "movie"}
#     try:
#         response = requests.get(API, params=params, timeout=5)
#         print(response.url)
#     except requests.exceptions.Timeout:
#         print("Timeout for API Request")
#         return None
#     except requests.exceptions.RequestException as e:
#         print(f"API Request failed: {e}")
#         return None
#
#     return response
#
# def validate_and_parse_api_response(
#         movie_info: dict[str, str]
#     ) -> dict[str, str|int|float|None] | None:
#     """Validates the response object and return the extracted movie data."""
#     if movie_info.get("Response") != "True":
#         print("Your movie could not be found")
#         return None
#
#     title = movie_info.get("Title")
#     if not title:
#         print("API Response invalid")
#         return None
#
#     try:
#         imdb_rating = float(movie_info.get("imdbRating"))
#     except (ValueError, TypeError):
#         print("Invalid IMDb-Rating! The movie can not be saved")
#         return None
#
#     try:
#         year = int(movie_info.get("Year"))
#     except (ValueError, TypeError):
#         print("Invalid Year! The movie can not be saved")
#         return None
#
#     poster_url = movie_info.get("Poster")
#
#     if poster_url:
#         poster_url = poster_url.strip()
#
#     if not poster_url or poster_url == "N/A":
#         print("No poster for this movie was found")
#         poster_url = None
#
#     imdb_id = movie_info.get("imdbID")
#     if not imdb_id:
#         print("No IMDb ID was found")
#
#     return {
#         "title": title,
#         "year": year,
#         "imdb_rating": imdb_rating,
#         "poster_url": poster_url,
#         "imdb_id": imdb_id
#     }
#
#
# def add_movie(user_name: str) -> None:
#     """Search for movies with the API
#     Select a movie if matching movies found.
#     Add the movie to the users profile."""
#     imdb_id = select_movie_from_api_search()
#     if imdb_id is None:
#         return
#
#     movie_response = get_movie_api_response(imdb_id)
#
#     if movie_response is None:
#         return
#
#     if movie_response.status_code != 200:
#         print(f"The API request failed with status code {movie_response.status_code}")
#         return
#
#     try:
#         movie_info = movie_response.json()
#     except ValueError:
#         print("API Request invalid")
#         return
#
#     movie_data = validate_and_parse_api_response(movie_info)
#
#     if movie_data is None:
#         return
#
#     storage.save_movie(
#         user_name,
#         movie_data["title"],
#         movie_data["year"],
#         movie_data["imdb_rating"],
#         movie_data["poster_url"],
#         movie_data["imdb_id"]
#         )
#
#
# def select_movie_from_api_search() -> str | None:
#     """Searches for similar movies in the API Database.
#     User chooses a movie, if there are movies found."""
#     search_title = input("Enter the movie title: ").strip()
#     if not search_title:
#         print("Enter a valid title.")
#         return None
#
#     response = get_search_api_response(search_title)
#     if response is None:
#         return None
#     movie_info = response.json()
#
#     if movie_info.get("Response") != "True":
#         print(f"No movies matching '{search_title}' found")
#         return None
#
#     title_matches = movie_info["Search"]
#
#     if len(title_matches) == 1:
#         movie_data = title_matches[0]
#         return movie_data["imdbID"]
#
#     print("0: Exit")
#     for index, movie_data in enumerate(title_matches, 1):
#         print(f"{index}. {movie_data['Title']} ({movie_data['Year']})")
#
#     while True:
#         try:
#             user_choice = int(input("Choose the correct movie: ").strip())
#             if user_choice == 0:
#                 return None
#             if 1 <= user_choice <= len(title_matches):
#                 break
#             print(f"Enter a number between 1 and {len(title_matches)}.")
#         except ValueError:
#             print("Enter a valid number.")
#
#     selected_movie = title_matches[user_choice - 1]
#     return selected_movie["imdbID"]
#
#
# def get_movie_api_response(imdb_id) -> requests.Response | None:
#     params = {"apikey": API_KEY, "i": imdb_id}
#     try:
#         response = requests.get(API, params=params, timeout=5)
#         print(response.url)
#         print(response.json())
#     except requests.exceptions.Timeout:
#         print("Timeout for API Request")
#         return None
#     except requests.exceptions.RequestException as e:
#         print(f"API Request failed: {e}")
#         return None
#
#     return response
#
# #
# # def get_all_titles(search_title):
# #     movie_response = (get_api_response(search_title))
# #     movie_info = movie_response.json()
# #     print(movie_info)
# #     title_matches = movie_info["Search"]
# #     if not title_matches:
# #         print(f"No movies with '{search_title}' found")
# #         return None
# #
# #     if len(title_matches) == 1:
# #         movie = title_matches[0]
# #         return movie["Title"]
# #
# #     print("0: Exit")
# #     for index, movie_data in enumerate(title_matches, 1):
# #         print(f"{index}. {movie_data['Title']} ({movie_data['Year']})")
# #
# #     while True:
# #         try:
# #             user_choice = int(input("Choose the correct movie: ").strip())
# #             if user_choice == 0:
# #                 return None
# #             if 1 <= user_choice <= len(title_matches):
# #                 break
# #             print(f"Enter a number between 1 and {len(title_matches)}.")
# #         except ValueError:
# #             print("Enter a valid number.")
# #
# #     selected_movie = title_matches[user_choice - 1]
# #     return selected_movie["imdbID"]
# #
# #
# # def get_api_data(imdb_id) -> requests.Response | None:
# #     params = {"apikey": API_KEY, "i": imdb_id}
# #     try:
# #         response = requests.get(API, params=params, timeout=5)
# #         print(response.url)
# #         print(response.json())
# #     except requests.exceptions.Timeout:
# #         print("Timeout for API Request")
# #         return None
# #     except requests.exceptions.RequestException as e:
# #         print(f"API Request failed: {e}")
# #         return None
# #
# #     return response
# #
# # imdb_id = get_all_titles("Harry Potter")
# # print(imdb_id)
# # correct_movie = get_api_data(imdb_id)
# # print(correct_movie)
# # correct_movie_data = correct_movie.json()
# # print(correct_movie_data)
# #
# # #
# #
# # # def select_movie_for_search(user_name: str) -> str | None:
# # #     """Searches for similar movies in the users profile.
# # #     User chooses can choose movie, if there are movies found."""
# # #
# # #     search_title = input("Enter the movie title: ").strip()
# # #     if not search_title:
# # #         return None
# # #
# # #     title_matches = storage.search_movies_for_user(user_name, search_title)
# # #
# # #     if not title_matches:
# # #         print(f"No movies with '{search_title}' found")
# # #         return None
# # #
# # #     if len(title_matches) == 1:
# # #         movie = title_matches[0]
# # #         return movie["title"]
# # #
# # #     print("0: Exit")
# # #     for index, movie_data in enumerate(title_matches, 1):
# # #         print(f"{index}. {movie_data['title']} ({movie_data['year']})")
# # #
# # #     while True:
# # #         try:
# # #             user_choice = int(input("Choose the correct movie: ").strip())
# # #             if user_choice == 0:
# # #                 return None
# # #             if 1 <= user_choice <= len(title_matches):
# # #                 break
# # #             print(f"Enter a number between 1 and {len(title_matches)}.")
# # #         except ValueError:
# # #             print("Enter a valid number.")
# # #
# # #     selected_movie = title_matches[user_choice - 1]
# # #     return selected_movie["title"]
