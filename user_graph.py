"""CSC111 Winter 2026 Project 2: Anime Recommendation System (User Favourites)

Module Description
==================
This module implements the user-based graph recommendations. It models users and anime as vertices in a graph, where
edges represent if a user has favourited that anime. To recommend anime, it computes similarity between two users
using Jaccard similarity. It then takes the anime from the top <limit> users in terms of similarity score and
accumulates the similarity score of the top users per anime, returning a dictionary mapping the top anime to their
final, normalized scores.

This file is Copyright (c) 2026 Lily Annelise Canete-Goodine, Parmida Arab, Miray Ozdemir, Edwin Zeng
"""
from __future__ import annotations
import networkx as nx
import data_sanitization


class _Vertex:
    """A vertex in a graph, used to represent a user or an anime.

    Each vertex item is either a user id or anime title. Both are represented as strings.
    Copies CSC111 A3 _Vertex class.

    Instance Attributes:
        - item: The data stored in this vertex, representing a user or anime.
        - kind: The type of this vertex: 'user' or 'anime'.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'user', 'anime'}
    """
    item: str
    kind: str
    neighbours: set[_Vertex]

    def __init__(self, item: str, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'user', 'anime'}
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    def similarity_score(self, other: _Vertex) -> float:
        """Return the similarity score between this vertex and other.
        Implements similarity score using Jaccard similarity and intended usage in program is to find similarity between
        two users.

        """
        if self.degree() == 0 or other.degree() == 0:
            return 0
        return len(self.neighbours.intersection(other.neighbours)) / len(self.neighbours.union(other.neighbours))


def _normalize_scores(anime_to_score: dict[str, float]) -> dict[str, float]:
    """Return scores normalized to the range [0, 1]."""
    if anime_to_score == {}:
        return {}

    scores = list(anime_to_score.values())
    min_score = min(scores)
    max_score = max(scores)

    normalized_scores = {}
    for anime, score in anime_to_score.items():
        if max_score == min_score:
            normalized_scores[anime] = 1.0
        else:
            normalized_scores[anime] = (score - min_score) / (max_score - min_score)

    return normalized_scores


class Graph:
    """A graph used to represent a profile-anime network.
    Structure copied from CSC111 A3, added/modified methods include add_input_user, get_top_similar_users, 
    _get_candidate_anime, _score_candidate_anime, recommend_anime, and to_networkx.

    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item (anime title and user id) to its _Vertex object.
    _vertices: dict[str, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: str, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'user', 'anime'}
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_edge(self, item1: str, item2: str) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def add_input_user(self, inputted_anime: list[str], input_username: str) -> None:
        """
        Deletes existing vertex with item input_username if necessary, then adds a new one to represent the input user
        and their favourite anime.
        """
        if input_username in self._vertices:
            v = self._vertices[input_username]
            for neighbour in v.neighbours:
                neighbour.neighbours.remove(v)
            del self._vertices[input_username]
        self.add_vertex(input_username, "user")
        for anime in inputted_anime:
            self.add_vertex(anime, "anime")
            self.add_edge(anime, input_username)

    def adjacent(self, item1: str, item2: str) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: str) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'user', 'anime'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def get_similarity_score(self, item1: str, item2: str) -> float:
        """Return the similarity score between the two given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        >>> g = Graph()
        >>> for i in range(0, 6):
        ...     g.add_vertex(str(i), kind='user')
        >>> g.add_edge('0', '2')
        >>> g.add_edge('0', '3')
        >>> g.add_edge('0', '4')
        >>> g.add_edge('1', '3')
        >>> g.add_edge('1', '4')
        >>> g.add_edge('1', '5')
        >>> g.get_similarity_score('0', '1')
        0.5
        """
        if item1 in self._vertices and item2 in self._vertices:
            return self._vertices[item1].similarity_score(self._vertices[item2])
        raise ValueError

    def get_top_similar_users(self, inputted_username: str, limit_users: int) -> dict[str, float]:
        """Return up to <limit_users> top similar users by similarity score, mapped to similarity score."""
        neighbour_users_to_score = []
        for user_id in self.get_all_vertices(kind='user'):
            if user_id == inputted_username:
                continue
            sim_score = self.get_similarity_score(user_id, inputted_username)
            if sim_score != 0:
                neighbour_users_to_score.append((user_id, sim_score))
        neighbour_users_to_score.sort(key=lambda x: x[1], reverse=True)
        return dict(neighbour_users_to_score[:limit_users])

    def _get_candidate_anime(self, top_users: dict[str, float], inputted_anime: list[str]) -> set[str]:
        """Return anime watched by top users, excluding inputted anime."""
        candidate_anime = set()
        for username in top_users:
            candidate_anime.update(self.get_neighbours(username))
        candidate_anime.difference_update(set(inputted_anime))
        return candidate_anime

    def _score_candidate_anime(self, candidate_anime: set[str], top_users: dict[str, float]) -> dict[str, float]:
        """Return unnormalized recommendation scores for each candidate anime, gathered from the anime of the
        top similar users."""
        anime_to_score = {}
        for anime in candidate_anime:
            total_score = 0.0
            contributors = 0
            for user in self.get_neighbours(anime):
                if user in top_users:
                    contributors += 1
                    total_score += top_users[user]
            if total_score > 0:
                anime_to_score[anime] = total_score * (contributors / (contributors + 1))
        return anime_to_score

    def recommend_anime(self, inputted_anime: list[str], limit_anime: int = 20, limit_users: int = 50) \
            -> dict[str, float]:
        """Return a dict mapping recommended anime titles to their recommendation scores,
        in descending order of score, with at most <limit_anime> results.

        The returned dict keys does not contain:
            - the input anime itself
            - any anime with a similarity score of 0 to the input anime
            - any duplicates
            - any vertices that represents a user (instead of an anime)

        Up to <limit_anime> anime are returned, ordered from highest to lowest score.
        Fewer than <limit_anime> anime may be returned if not enough valid candidates exist.

        Preconditions:
            - all(anime in self._vertices for anime in inputted_anime)
            - all(self._vertices[anime].kind == 'anime' for anime in inputted_anime)
            - limit >= 1
        """
        self.add_input_user(inputted_anime, "inputted_user")
        top_users = self.get_top_similar_users("inputted_user", limit_users)
        candidate_anime = self._get_candidate_anime(top_users, inputted_anime)
        unnormalized_scores = self._score_candidate_anime(candidate_anime, top_users)
        normalized_scores = {}
        unnormalized_list = list(unnormalized_scores.values())
        min_score = min(unnormalized_list)
        max_score = max(unnormalized_list)
        for anime, score in unnormalized_scores.items():
            if max_score == min_score:
                normalized_scores[anime] = 1.0
            else:
                normalized_scores[anime] = (score - min_score) / (max_score - min_score)
        sorted_anime = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_anime[:limit_anime])

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph. Copied from CSC111 A3 handout.

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


def load_user_graph(user_file: str, anime_file: str) -> Graph:
    """Return a user and anime graph corresponding to the given datasets. Note: the graph loads
    every single user with at least two anime in their favourites list.

    Skips creating graph edges/vertices when user_file contains an anime that does not exist in the anime_file

    Preconditions:
        - user_file is the path to a CSV file corresponding to the user data
        - anime_file is the path to a CSV file corresponding to the anime data

    >>> g = load_user_graph('profiles_small.csv', 'animes_small.csv')
    >>> len(g.get_all_vertices(kind='anime'))
    12
    >>> len(g.get_all_vertices(kind='user'))
    12
    >>> user1 = g.get_neighbours('DesolatePsyche')
    >>> len(user1)
    4
    >>> "Code Geass: Hangyaku no Lelouch R2" in user1
    True
    """
    g = Graph()
    user_map = data_sanitization.clean_profiles(user_file)
    anime_map = data_sanitization.get_anime_id_title_map(anime_file, user_map)
    for user in user_map:
        g.add_vertex(user, "user")
        for anime in user_map[user]:
            try:
                anime_title = anime_map[anime]
                g.add_vertex(anime_title, "anime")
                g.add_edge(user, anime_title)
            except KeyError:
                continue
    return g


def load_custom_user_graph(num_top_users: int, total_graph: Graph, inputted_anime: list[str]) -> Graph:
    """Return a graph containing the inputted user, their inputted anime,
    the top similar users, and all anime adjacent to those users."""
    g = Graph()
    input_username = "inputted_user"
    total_graph.add_input_user(inputted_anime, input_username)
    top_users = total_graph.get_top_similar_users(input_username, num_top_users)
    g.add_vertex(input_username, "user")
    for input_anime in inputted_anime:
        g.add_vertex(input_anime, "anime")
        g.add_edge(input_anime, input_username)
    for user in top_users:
        g.add_vertex(user, 'user')
        for anime in total_graph.get_neighbours(user):
            g.add_vertex(anime, "anime")
            g.add_edge(user, anime)
    return g


if __name__ == '__main__':

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['networkx', 'data_sanitization'],
        'max-nested-blocks': 4
    })
