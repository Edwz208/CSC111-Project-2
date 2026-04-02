"""
Run this file to run the entire program from start to finish
"""
import anime_recs_gui
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
                               inputted_ratings: dict[str, int], limit: int) -> list[str]:
    """Calls the respective recommendation functions for attribute_graph, passes the outcome to
    combined_recommendation function
    """
    shows_user = list(inputted_ratings.keys())  # we are extracting titles given by user
    attribute_based_graph = attribute_graph.recommend_new_show(shows_user, limit)
    user_based_graph = rating_graph.recommend_anime_weighted(inputted_ratings, limit)

    final_recs = combined_recommendation(user_based_graph, attribute_based_graph, limit)
    if len(final_recs) < 3:
        if len(user_based_graph) > len(attribute_based_graph):
            return list(user_based_graph.keys())
        else:
            return list(attribute_based_graph.keys())
    else:
        return final_recs


if __name__ == "__main__":
    text_shell = QApplication(sys.argv)
    anime_recs_gui.load_stylesheet(text_shell)
    window = anime_recs_gui.MainWindow()
    window.show()
    sys.exit(text_shell.exec())
