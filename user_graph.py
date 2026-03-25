from __future__ import annotations
from typing import Any
from data_sanitization import clean_profiles, get_anime_id_title_map


class _Vertex:
    """A vertex in a graph, used to represent a user or an anime.

    Each vertex item is either a user id or anime title. Both are represented as strings.

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
            - kind in {'user', 'book'}
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    def similarity_score(self, other: _Vertex) -> float:
        """Return the similarity score between this vertex and other.
        """
        if self.degree() == 0 or other.degree() == 0:
            return 0
        return len(self.neighbours.intersection(other.neighbours)) / len(self.neighbours.union(other.neighbours))


class Graph:
    """A graph used to represent a profile-anime network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[str, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: str, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'user', 'book'}
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def delete_vertex(self, item: str) -> None:
        """Delete a vertex with the given item from the graph"""
        if item in self._vertices:
            del self._vertices[item]

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
            - kind in {'', 'user', 'book'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def get_similarity_score(self, item1: Any, item2: Any) -> float:
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

    def recommend_anime(self, inputted_anime: list[str], limit_anime: int, limit_users: int) -> list[str]:
        """Return a list of up to <limit> recommended anime based on similarity to the given user based on the inputted
        list of anime. It takes the top anime from the top limit_users in similarity scores and then gives each one a
        new score by accumulating sim_score from user for every user that watched the anime.

        The return value is a list of the titles of recommended books, sorted in
        *descending order* of similarity score. Ties are ignored for now.

        The returned list should NOT contain:
            - the input anime itself
            - any anime with a similarity score of 0 to the input anime
            - any duplicates
            - any vertices that represents a user (instead of an anime)

        Up to <limit> anime are returned, starting with the anime with the highest similarity score,
        then the second-highest similarity score, etc. Fewer than <limit> anime are returned if
        and only if there aren't enough anime that meet the above criteria.

        Preconditions:
            - anime in self._vertices
            - self._vertices[anime].kind == 'anime'
            - limit >= 1
            - all(anime in self._vertices for anime in inputted_anime)
        """
        # Create a user based on inputted anime
        self.delete_vertex("inputted_user")
        self.add_vertex("inputted_user", "user")
        for anime in inputted_anime:
            self.add_edge("inputted_user", anime)

        neighbour_users_to_score = []
        for user_id in self.get_all_vertices(kind='user'):
            sim_score = self.get_similarity_score(user_id, "inputted_user")
            if sim_score != 0 and user_id != "inputted_user":
                neighbour_users_to_score.append((user_id, sim_score))
        neighbour_users_to_score.sort(key=lambda x: x[1], reverse=True)
        top_users = {username: score for username, score in neighbour_users_to_score[:limit_users]}
        top_anime = set()
        for username in top_users:
            top_anime = top_anime.union(self.get_neighbours(username))

        anime_new_score = []
        for anime in top_anime:
            for user in self.get_neighbours(anime):
                if user in top_users:
                    anime_new_score.append((anime, top_users[user]))
        anime_new_score.sort(key=lambda x: x[1], reverse=True)
        return anime_new_score[:limit_anime]


def load_user_graph(user_file: str, anime_file: str) -> Graph:
    """Return a user and anime graph corresponding to the given datasets. Note: the graph loads
    every single anime that has at least one user who favourited it.

    Preconditions:
        - user_file is the path to a CSV file corresponding to the user data
        - anime_file is the path to a CSV file corresponding to the anime data
        - every favourite anime in user_file is an existing anime in the anime data

    >>> g = load_user_graph('data/profiles_small.csv', 'data/animes_small.csv')
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
    user_map = clean_profiles(user_file)
    anime_map = get_anime_id_title_map(anime_file, user_map)
    for user in user_map:
        g.add_vertex(user, "user")
        for anime in user_map[user]:
            anime_title = anime_map[anime]
            g.add_vertex(anime_title, "anime")
            g.add_edge(user, anime_title)

    return g


if __name__ == '__main__':
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
