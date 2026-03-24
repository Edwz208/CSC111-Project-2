from __future__ import annotations
import csv
from typing import Any


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
    Currently does not sanitize, just returns the list from csv file
    """
    user_list = []
    user_ids = set()
    with open(profiles_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if row[0] not in user_ids:
                user_list.append({"profile": row[0], "favourite_anime": [row[3]]})
    return user_list


if __name__ == "__main__":
    print(clean_profiles("data/profiles_small.csv"))
