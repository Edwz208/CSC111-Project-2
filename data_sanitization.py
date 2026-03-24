from __future__ import annotations
import csv
from typing import Any
import ast


def clean_anime(anime_file) -> list[dict[str, Any]]:
    """
    Return a list of anime, with each one being a dictionary mapping of its attributes
    Currently does not sanitize, just returns list
    """
    anime_list = []
    anime_ids = set()
    with open(anime_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if row[0] not in anime_ids:
                anime_list.append({"id": row[0], "title": row[1], "synopsis": row[2],"genre": row[3],
                                   "aired": row[4], "episodes": row[5], "members": row[6], "popularity": row[7],
                                   "ranked": row[8], "score": row[9]})
    return anime_list


def clean_profiles(profiles_file) -> list[dict[str, Any]]:
    """
    Return a list of user profiles, with each one being a dictionary mapping of its attributes
    Gets rid of duplicate user profiles, duplicate anime ids within a favourite anime list, and skips users entirely
    if the user has invalid anime id.
    """
    user_list = []
    user_ids = set()
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
            if user_id not in user_ids and favourites_clean != []:
                user_list.append({"profile": user_id, "favourite_anime": favourites_clean})
                user_ids.add(user_id)
    return user_list


if __name__ == "__main__":
    print(clean_profiles("data/profiles_small.csv"))
