"""CSC111 Winter 2026 Project 2: Anime Recommendation System (User Reviews)

Module Description
==================
This module runs the recommendation system.  It loads the attribute-based, unweighted and weighted user-rating graphs,
combines their recommendations, and launches the graphical user interface.

This file is Copyright (c) 2026 Lily Annelise Canete-Goodine, Miray Ozdemir, Parmida Arab, Edwin Zeng


"""
import anime_recommendations_gui
from user_rating_graph import WeightedGraph
from attribute_graph import Graph
import sys
from PySide6.QtWidgets import QApplication


def combined_recommendation(user_recs: dict[str, float], attribute_recs: dict[str, float], returned_limit) -> list[str]:
    """
    Returns a final list of anime titles based on the user-based recommendation and attribute-based recommendation and
    combining them. The final list has a chosen number returned.

    Up to <limit> anime are returned, starting with the anime with the highest similarity score,
    then the second-highest similarity score, etc. Fewer than <limit> anime are returned if
    and only if there aren't enough anime that meet the criteria.

    If the combination of recommendations is fewer than three, returns the user-/attribute-based recommendation
    with the longer list of recommendations.
    """
    COEFFICIENT = 0.3
    anime_final_score = {}
    for anime in user_recs:
        if anime in attribute_recs:
            combined_score = COEFFICIENT * user_recs[anime] + (1 - COEFFICIENT) * attribute_recs[anime]
            if combined_score > 0:
                anime_final_score[anime] = combined_score
    sorted_anime = sorted(anime_final_score.items(), key=lambda x: x[1], reverse=True)
    return [anime for anime, score in sorted_anime[:returned_limit]]


def call_graphs_and_transform(attribute_graph: Graph, rating_graph: WeightedGraph,
                               inputted_ratings: dict[str, int], returned_limit: int) -> list[str]:

    """Return a recommendation list of up to <returned_limit> anime titles by calling both the attribute-based
     and user-rating recommendation functions and combining their results.
     The input anime titles are extracted from <inputted_ratings> and passed to the attribute graph,
     and the ratings dictionary is passed to the weighted user-rating graph.
     The results are combined using combined_recommendation().
     If the combined result contains fewer than 3 titles,
     the longer of the two individual recommendation lists is returned instead.

    Preconditions:

    - returned_limit >= 1
    - all(anime in attribute_graph._vertices for anime in inputted_ratings)
     - all(anime in rating_graph._vertices for anime in inputted_ratings)
     """

    shows_user = list(inputted_ratings.keys())  # we are extracting titles given by user
    attribute_based_graph = attribute_graph.recommend_new_show(shows_user, returned_limit)
    user_based_graph = rating_graph.recommend_anime_weighted(inputted_ratings, returned_limit)

    final_recs = combined_recommendation(user_based_graph, attribute_based_graph, returned_limit)
    if len(final_recs) < 3:
        if len(user_based_graph) > len(attribute_based_graph):
            return list(user_based_graph.keys())
        else:
            return list(attribute_based_graph.keys())
    else:
        return final_recs


if __name__ == "__main__":
    text_shell = QApplication(sys.argv)
    window = anime_recommendations_gui.MainWindow()
    window.load_stylesheet(text_shell)
    window.show()
    sys.exit(text_shell.exec())
