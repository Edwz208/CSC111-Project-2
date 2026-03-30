from __future__ import annotations
import csv
from typing import Any
import ast
import pandas as pd


def clean_anime(anime_file: str) -> list[dict[str, Any]]:
    """
    Return a list of anime, with each one being a dictionary mapping of its attributes
    Currently does not other than ensuring that title and id pairings are unique.
    IMPORTANT: DOES NOT WORK RIGHT NOW DUE TO SYNPSOSIS STRETCHING BEYOND A SINGLE LINE
    """
    # anime_list = []
    # anime_title_and_id = set()
    # with open(anime_file, mode='r', newline='') as file:
    #     reader = csv.reader(file)
    #     next(reader)
    #     for row in reader:
    #         anime_id = row[0]
    #         title = row[1]
    #         if (anime_id, title) not in anime_title_and_id:
    #             anime_title_and_id.add((anime_id, title))
    #             anime_list.append({"id": anime_id, "title": title, "synopsis": row[2], "genre": row[3],
    #                                "aired": row[4], "episodes": row[5], "members": row[6], "popularity": row[7],
    #                                "ranked": row[8], "score": row[9]})
    # return anime_list
    raise NotImplementedError


def clean_profiles(profiles_file: str) -> dict[str, list[int]]:
    """
    Return a mapping of user profiles to their favourite_anime
    Gets rid of duplicate user profiles, duplicate anime ids within a favourite anime list, and skips users entirely
    if the user has invalid anime id.
    """
    user_map = {}
    USER_MINIMUM_FAVOURITES = 2
    with open(profiles_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            user_id = row[0]
            user_favourites = ast.literal_eval(row[3])
            anime_ids = set()
            favourites_clean = []
            for anime in user_favourites:
                try:
                    anime_id = int(anime)
                except ValueError:
                    favourites_clean = []
                    break
                if anime_id not in anime_ids:
                    anime_ids.add(anime_id)
                    favourites_clean.append(anime_id)
            if user_id not in user_map and len(favourites_clean) >= USER_MINIMUM_FAVOURITES:
                user_map[user_id] = favourites_clean
    return user_map


def get_anime_id_title_map(anime_file: str, user_map: dict[str, list[int]] | dict[str, list[tuple[int, int]]]) -> dict[int, str]:
    """
    Return a dictionary mapping an anime integer id to its string title. It skips duplicates of an anime and filters out
    anime which are not in a list of favourite from the users. It takes in two variations of user_map data to support
    both weighted and unweighted graphs.
    """
    anime_ids_from_user = set()
    for username in user_map:
        for item in user_map[username]:
            if isinstance(item, tuple):
                anime = item[0]
            else:
                anime = item
            anime_ids_from_user.add(anime)

    df = pd.read_csv(anime_file)
    anime_map = {}
    for _, row in df.iterrows():
        try:
            anime_id = int(row['uid'])
            title = str(row['title'])
        except ValueError:
            continue
        if anime_id not in anime_map and anime_id in anime_ids_from_user:
            anime_map[anime_id] = title
    return anime_map


def clean_ratings(ratings_file: str) -> dict[str, list[tuple[int, int]]]:
    """
    Return a mapping of user ratings to the anime they reviewed.
    Gets rid of duplicate user to anime pairings within a rating list from a user, and skips any rating
    if the user has rated a non-integer anime id. It also gets rid of all users who have less than the minimum number of
    reviews required.
    """
    user_map = {}
    USER_MINIMUM_REVIEWS = 3
    df = pd.read_csv(ratings_file)
    user_anime_id = set()
    for _, row in df.iterrows():
        try:
            user_id = str(row['profile'])
            rating = int(row['score'])
            anime_id = int(row['anime_uid'])
        except ValueError:
            continue
        if (user_id, anime_id) not in user_anime_id:
            if user_id not in user_map:
                user_map[user_id] = []
            user_map[user_id].append((anime_id, rating))
            user_anime_id.add((user_id, anime_id))
    filtered_user_map = {}
    for user in user_map:
        if len(user_map[user]) >= USER_MINIMUM_REVIEWS:
            filtered_user_map[user] = user_map[user]
    return filtered_user_map


if __name__ == "__main__":
    pass
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()
    #
    # import doctest
    # doctest.testmod()
    #
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': ['csv', 'networkx'],
    #     'allowed-io': ['load_review_graph'],
    #     'max-nested-blocks': 4
    # })
