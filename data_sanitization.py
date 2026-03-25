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
            for i in range(len(user_favourites)):
                try:
                    if user_favourites[i] not in anime_ids:  # skip duplicate anime ids
                        anime_ids.add(user_favourites[i])
                        favourites_clean.append(int(user_favourites[i]))
                except ValueError:
                    favourites_clean = []
                    break  # skip this user
            if user_id not in user_map and len(favourites_clean) >= USER_MINIMUM_FAVOURITES:
                user_map[user_id] = favourites_clean
    return user_map


def get_anime_id_title_map(anime_file: str, user_map: dict[str, list[int]]) -> dict[int, str]:
    """
    Return a dictionary mapping an anime integer id to its string title. It skips duplicates of an anime and filters out
    anime which are not in a list of favourite from the users
    """
    anime_ids_from_user = set()
    for username in user_map:
        for anime in user_map[username]:
            anime_ids_from_user.add(anime)

    df = pd.read_csv(anime_file)
    anime_map = {}
    for _, row in df.iterrows():
        anime_id = int(row['uid'])
        title = row['title']
        if anime_id not in anime_map and anime_id in anime_ids_from_user:
            anime_map[anime_id] = title
    return anime_map


def remove_under_favourites_lower_bound(list_of_users: dict[str, list[int]], limit: int) -> dict[str, list[int]]:
    """
    Given a list of user dictionaries, return the list with only those that have a number of favourite anime above the
    inputted integer.
    """
    new_users = {}
    for user in list_of_users:
        if len(list_of_users[user]) >= limit:
            new_users[user] = list_of_users[user]
    return new_users


if __name__ == "__main__":
    user_mapping = clean_profiles("data/profiles_small.csv")
    print(user_mapping)
    print(get_anime_id_title_map("data/animes_small.csv", user_mapping))
