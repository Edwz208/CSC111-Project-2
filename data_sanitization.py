"""CSC111 Winter 2026 Project 2: Anime Recommendation System (Data Handling)

Module Description
==================
This module provides functions for cleaning and organizing anime-related datasets used
in an anime recommendation system. It processes raw CSV data containing user profiles, user reviews, and anime metadata,
transforming it into datatypes required for further analysis. All functions ensure data integrity for consistency
in the data by handling invalid entries, removing duplicates, and checking for minimum number thresholds.

This file is Copyright (c) 2026 Lily Annelise Canete-Goodine, Parmida Arab, Miray Ozdemir, Edwin Zeng
"""
from __future__ import annotations
import csv
import ast


def clean_profiles(profiles_file: str) -> dict[str, list[int]]:
    """
    Return a mapping of user profiles a list of the ids of their favourite anime.

    In the case of duplicate user profiles, only keeps the initial favourites list for the user.
    Gets rid of duplicate anime ids within a favourite anime list.
    Skips anime ids that cannot be converted into integer format.
    Gets rid of all users who have a list of favourites less than or equal to the
    internally set _user_minimum_favourites.

    Preconditions:
        - profiles_file is the path to a CSV file corresponding to the user profile data, formatted where user ids are
        the first column and user favourites are the string representations of a list in the fourth column.
    """
    user_map = {}
    _user_minimum_favourites = 2
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
                    if anime_id not in anime_ids:
                        anime_ids.add(anime_id)
                        favourites_clean.append(anime_id)
                except ValueError:
                    continue
            if user_id not in user_map and len(favourites_clean) >= _user_minimum_favourites:
                user_map[user_id] = favourites_clean
    return user_map


def clean_reviews(reviews_file: str) -> dict[str, list[tuple[int, int]]]:
    """
    Return a mapping of user ids to a list of tuples of format (anime_id, rating).

    In the case of duplicate user to anime reviews, only keeps the initial rating for this anime from the user.
    Gets rid of duplicate anime ids within a favourite anime list.
    Skips reviews where the anime id or rating/score cannot be converted into integer format.
    Gets rid of all users who have a cleaned list of written reviews less than or equal to the
    internally set _user_minimum_reviews.

    Preconditions:
        - reviews_file is the path to a CSV file corresponding to the user reviews data, formatted where user ids are
        the second column, anime ids are in the third column, and scores/ratings are in the 5th column.
    """
    user_map = {}
    _user_minimum_reviews = 2
    user_anime_id = set()
    with open(reviews_file, mode='r', newline='', encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            try:
                user_id = row[1]
                anime_id = int(row[2])
                rating = int(row[4])
                if (user_id, anime_id) not in user_anime_id:
                    user_anime_id.add((user_id, anime_id))
                    if user_id not in user_map:
                        user_map[user_id] = []
                    user_map[user_id].append((anime_id, rating))
            except ValueError:
                continue
    filtered_user_map = {}
    for user in user_map:
        if len(user_map[user]) >= _user_minimum_reviews:
            filtered_user_map[user] = user_map[user]
    return filtered_user_map


def get_anime_id_title_map(anime_file: str, user_map: dict[str, list[int]] | dict[str, list[tuple[int, int]]]) \
        -> dict[int, str]:
    """
    Return a dictionary mapping an anime integer id to its string title.

    In the case of duplicate anime ids from anime_file, only keeps the initial title from the first row in the data.
    Skips animes where the anime id cannot be converted into integer format.
    Skips any anime that are not in the anime ids extracted from user_map.
    It takes in two variations of user_map data to support datatype from cleaning both review and profile files,
    returning only valid anime according to the possible data from the user.

    Preconditions:
        - anime_file is the path to a CSV file corresponding to the anime data, formatted where anime ids are
        the first column, and anime titles are the second column.
        - user_map contains anime ids from a reviews file or profiles file which correponds
        to the anime ids in anime_file.
    """
    anime_ids_from_user = set()
    for username in user_map:
        for item in user_map[username]:
            if isinstance(item, tuple):
                anime = item[0]
            else:
                anime = item
            anime_ids_from_user.add(anime)

    anime_map = {}
    with open(anime_file, mode='r', newline='', encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            try:
                anime_id = int(row[0])
                title = row[1]
                if anime_id not in anime_map and anime_id in anime_ids_from_user:
                    anime_map[anime_id] = title
            except ValueError:
                continue
    return anime_map


if __name__ == "__main__":
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()
    import doctest
    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['csv', 'ast'],
        'allowed-io': ['clean_profiles', 'clean_reviews', 'get_anime_id_title_map'],
        'max-nested-blocks': 4
    })
