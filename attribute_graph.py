"""CSC111 Project 2: Anime Recommendation System - Attribute Based Graph

This Python module is an anime recommendation system, using a graph that models the
relationship of shows and their attributes like genre, popularity, and score;
and Jaccard similarity to calculate the similarity between the anime shows.

This file is Copyright (c) 2026 Miray Ozdemir, Lily Annelise Canete-Goodine, Parmida Arab, Edwin Zeng

"""

from __future__ import annotations
import csv
import ast
from typing import Any

import networkx as nx


class _Vertex:
    """A vertex in an anime show data graph, used to represent a show or an attribute.

    Each vertex item is either a show title or an attribute.
    Attributes will be:
    - genre
    - popularity
    - score
    Both the show title and attributes are represented as strings.

    Instance Attributes:
        - item: The data stored in this vertex represents a show, or an attribute.
        - kind: The type of this vertex. It can be; 'title', 'genre', 'score', 'popularity'.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'title', 'genre', 'popularity', 'score'}
    """
    item: Any
    kind: str
    neighbours: set[_Vertex]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This initialized vertex has no neighbours.

        Preconditions:
            - kind in {'title', 'genre', 'popularity', 'score'}
        """

        self.item = item
        self.kind = kind
        self.neighbours = set()

    def similarity_score(self, other: _Vertex) -> float:
        """This function returns the Jaccard similarity score between this and the given vertex in float type.
        The similarity score gets calculated by calculating the ratio between the two vertices' intersection and union.
        The result will be a float between 0 and 1.
        If either vertex does not have any neighbours, then the similarity score will be 0.

        """

        if not self.neighbours or not other.neighbours:
            return 0

        else:
            intersection_calc = self.neighbours.intersection(other.neighbours)
            union_calc = self.neighbours.union(other.neighbours)

            return len(intersection_calc) / len(union_calc)


class Graph:
    """A graph used to represent show-attribute relationships.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.

    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph without any vertices or edges.
        """

        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.
        The initialized vertex has no neighbours. Do nothing if the given item is already existing this graph.

        Preconditions:
            - kind in {'title', 'genre', 'popularity', 'score'}
        """

        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2

        >>> graph = Graph()
        >>> graph.add_vertex("Sailor Moon", "title")
        >>> graph.add_vertex("Mahou Shoujo", "genre")
        >>> graph.add_edge("Sailor Moon", "Mahou Shoujo")
        >>> "Mahou Shoujo" in graph.get_neighbours("Sailor Moon")
        True

        """
        if item1 not in self._vertices or item2 not in self._vertices:
            raise ValueError

        else:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)

    def get_neighbours(self, item: Any) -> dict[str, str]:
        """Return a dict of the neighbours items to their corresponding kind for the given item.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item: neighbour.kind for neighbour in v.neighbours}
        else:
            raise ValueError

    @staticmethod
    def get_all_attribute(i: int, anime_data: str) -> set:
        """
        This function will collect all the attributes in given index in a set.
        Raise a ValueError if the given index i is out of bounds in csv rows.

                - uid = row[0]
                - title = row[1]
                - genre = row[3]
                - popularity = row[7]
                - score = row[9]
        """
        with open(anime_data) as file:
            reader = csv.reader(file)
            next(reader)

            attributes = set()
            for row in reader:
                if i >= len(row):
                    raise ValueError("index is out of bounds")
                attributes.add(row[i])
            return attributes

    def get_all_vertices(self, kind: str = '') -> set:
        """The function will return a set of all vertex items of the given kind.

        If the kind is not given, the function will return everything.

        Preconditions:
            - kind in {'title', 'genre', 'popularity', 'score'}

        >>> le_graph = Graph()
        >>> le_graph.add_vertex("Sailor Moon", "title")
        >>> le_graph.add_vertex("Mahou Shoujo", "genre")
        >>> le_graph.get_all_vertices("title")
        {'Sailor Moon'}
        """
        if kind == '':
            return set(self._vertices.keys())
        else:
            return {v.item for v in self._vertices.values() if v.kind == kind}

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Converts this graph into a networkx Graph. Adapted from CSC111 A3 handout.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(v.item, kind=v.kind)
            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u.item, kind=u.kind)

                if u.item in graph_nx.nodes:
                    graph_nx.add_edge(v.item, u.item)
            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    def get_similarity_score(self, item1: Any, item2: Any) -> float:
        """Return the Jaccard similarity score between the given items, item1 and item2, in this graph.

        If the vertices item1 or item2 do not appear in this graph, raise a ValueError .


        >>> le_graph = Graph()
        >>> le_graph.add_vertex("Sailor Moon", "title")
        >>> le_graph.add_vertex("Mahou Shoujo", "genre")
        >>> le_graph.add_vertex("Frieren", "title")
        >>> le_graph.add_vertex("action", "genre")
        >>> le_graph.add_vertex("comedy", "genre")
        >>> le_graph.add_vertex("Mob Psycho", "title")
        >>> le_graph.add_edge("Mob Psycho", "action")
        >>> le_graph.add_edge("Mob Psycho", "comedy")
        >>> le_graph.add_edge("Frieren", "action")
        >>> le_graph.add_edge("Sailor Moon", "Mahou Shoujo")
        >>> le_graph.get_similarity_score("Frieren", "Mob Psycho")
        0.5

        """
        if item1 not in self._vertices or item2 not in self._vertices:
            raise ValueError

        else:
            return self._vertices[item1].similarity_score(self._vertices[item2])

    def find_closes_title(self, show: str) -> str:
        """
        Return the show that has a similar name as the given input, by finding the first vertex title
        the function encounters that contains the given show as a substring.
        Function is case-insensitive, and returns an empty string if no match is found.

        """
        lowered_input = show.lower().strip()
        all_shows = self.get_all_vertices(kind="title")

        for each_show in all_shows:
            if lowered_input in each_show.lower():
                return each_show
        return ""

    def get_top_similar_anime(self, inputted_anime: str, limit_anime: int) -> list[str]:
        """Return up to <limit_anime> top similar anime by similarity score"""
        neighbour_anime_to_score = []
        for anime_title in self.get_all_vertices(kind='title'):
            if anime_title == inputted_anime:
                continue
            sim_score = self.get_similarity_score(anime_title, inputted_anime)
            if sim_score != 0:
                neighbour_anime_to_score.append((anime_title, sim_score))
        neighbour_anime_to_score.sort(key=lambda x: x[1], reverse=True)
        return list(score_pair[0] for score_pair in neighbour_anime_to_score[:limit_anime])

    def recommend_new_show(self, shows: list[str], limit_anime: int) -> dict[str, float]:
        """
        This function returns a dict of recommended shows, with a length of no more than "limit_anime",
        sorted by the similarity scores. The recommendations are based on the jaccard similarity between
        a potential show and all inputted shows in "shows" list.Shows that are already in the inputted list
        is/are excluded from the final recommendations.
        Dictionary goes from the show that has the highest similarity to lowest similarity,
         and the output does not exceed the given limit.

        Preconditions:
            - all( show in self._vertices for show in shows)
            - all( self._vertices[show].kind == 'title', for show in shows)
            - limit_anime >= 1
        """

        corrected_shows = []
        for show in shows:
            if show in self._vertices:
                corrected_shows.append(show)
            else:
                closest_title = self.find_closes_title(show)
                if closest_title != "":
                    corrected_shows.append(closest_title)
                else:
                    raise ValueError

        all_shows = self.get_all_vertices(kind="title")
        for show in corrected_shows:
            if show in all_shows:
                all_shows.remove(show)

        scores_so_far = {}

        for the_show in all_shows:
            total_score = 0
            for show in corrected_shows:
                total_score += self.get_similarity_score(the_show, show)
            average = total_score / len(corrected_shows)
            if average > 0:
                scores_so_far[the_show] = round(average, 2)

        scores_so_far = sorted(scores_so_far.items(), key=lambda x: x[1], reverse=True)

        recommendation_dict = {}
        for show_title, show_score in scores_so_far[:limit_anime]:
            recommendation_dict[show_title] = show_score

        return recommendation_dict


def score_range_helper(score: float) -> str:
    """
    Return the range of the score as a string of the given float score.
    Later these labels will be used as attribute vertices in the graph.

    >>> score_range_helper(8.5)
    '8-9'
    """
    if score >= 9.0:
        return '9-10'
    elif score >= 8.0:
        return '8-9'
    elif score >= 7.0:
        return '7-8'
    elif score >= 6.0:
        return '6-7'
    else:
        return '0-6'


def popularity_range_helper(popularity: float) -> str:
    """
    Return the range of the popularity as a string of the given float popularity value.
    Later these labels will be used as attribute vertices in the graph.

    >>> popularity_range_helper(111)
    '100-200'
    """
    if popularity < 100:
        return "0-100"
    elif popularity < 200:
        return "100-200"
    elif popularity < 300:
        return "200-300"
    elif popularity < 400:
        return "300-400"
    elif popularity < 500:
        return "400-500"
    else:
        return "500+"


def load_the_graph(anime_data: str) -> Graph:
    """Return a show-attribute relationship graph corresponding to the given csv dataset.
    Graph stores a vertex for each show and attributes.
    Use the "kind" _Vertex attribute to differentiate between different vertex types.
    Shows stored with kind="title", and attributes with kind="genre", "popularity",
    or "score".
    The show title vertices can not have an edge betwen them, nor can attribute vertices;
    A show vertex and an attribute vertex can have an edge between them.
    Edges represent the relationship between a show and an attribute. In this graph, each edge
    represents the existence of a relation.
    Preconditions:
        - anime_data is the path to a CSV file corresponding to the relevant anime data.
        - uid = row[0]
        - title = row[1]
        - genre = row[3]
        - popularity = row[7]
        - score = row[9]
    """
    show_attribute_graph = Graph()
    shows = {}
    with open(anime_data, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) >= 10 and row[9] != '':
                uid = row[0]
                title = row[1]
                genres = ast.literal_eval(row[3])
                popularity = popularity_range_helper(float(row[7]))
                score = score_range_helper(float(row[9]))
                shows[uid] = title
                show_attribute_graph.add_vertex(title, "title")
                show_attribute_graph.add_vertex(popularity, "popularity")
                show_attribute_graph.add_vertex(score, "score")
                for genre in genres:
                    show_attribute_graph.add_vertex(genre, "genre")
                    show_attribute_graph.add_edge(title, genre)

                show_attribute_graph.add_edge(title, popularity)
                show_attribute_graph.add_edge(title, score)

        return show_attribute_graph


def load_custom_attribute_graph(num_top_anime: int, total_graph: Graph,
                                inputted_anime: list[str]) -> Graph:
    """Return a graph containing the inputted anime, the most similar anime to each inputted anime, and
    all attribute vertices adjacent to those anime.
    """
    g = Graph()
    if not inputted_anime:
        return g
    anime_to_include = set()
    title_vertices = total_graph.get_all_vertices(kind='title')
    per_anime_limit = (num_top_anime // len(inputted_anime)) + 1
    for anime in inputted_anime:
        if anime in title_vertices:
            anime_to_include.add(anime)
            similar_anime = total_graph.get_top_similar_anime(anime, per_anime_limit)
            anime_to_include.update(similar_anime)
    for anime in anime_to_include:
        g.add_vertex(anime, 'title')
        for neighbour in total_graph.get_neighbours(anime):
            neighbour_kind = total_graph.get_neighbours(anime)[neighbour]
            if neighbour_kind == 'genre':
                g.add_vertex(neighbour, neighbour_kind)
                g.add_edge(anime, neighbour)
    return g


if __name__ == '__main__':
    import python_ta.contracts

    python_ta.contracts.check_all_contracts()

    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['csv', 'a3_part1', 'ast', 'networkx'],
        'allowed-io': ['load_the_graph', 'Graph.get_all_attribute'],
        'max-nested-blocks': 4
    })
