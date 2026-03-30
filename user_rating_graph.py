"""Module imports (docstring required)?"""
from __future__ import annotations
import data_sanitization


class _WeightedVertex:
    """A vertex in a weighted graph, used to represent a user or an anime.

    Each vertex item is either a user id or anime title. Both are represented as strings.
    Neighbours are now a dictionary mapping from a neighbour vertex to the weight of the edge to from self to
    that neighbour.

    Instance Attributes:
        - item: The data stored in this vertex, representing a user or anime.
        - kind: The type of this vertex: 'user' or 'anime'.
        - neighbours: The vertices that are adjacent to this vertex and the edges contain the corresponding weights.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'user', 'anime'}
    """
    item: str
    kind: str
    neighbours: dict[_WeightedVertex, int]

    def __init__(self, item: str, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'user', 'book'}
        """
        self.item = item
        self.kind = kind
        self.neighbours: dict[_WeightedVertex, int] = {}

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    def similarity_score_unweighted(self, other: _WeightedVertex) -> float:
        """Return the similarity score between this vertex and other, without using the edge weights.
        """
        if self.degree() == 0 or other.degree() == 0:
            return 0
        return (len(set(self.neighbours.keys()).intersection(other.neighbours))
                / len(set(self.neighbours.keys()).union(other.neighbours)))

    def similarity_score_weighted(self, other: _WeightedVertex) -> float:
        """Return the strict weighted similarity score between this vertex and other.
        Utilizes pearson correlction coefficient.
        Returns 0 if:
            - the users have less than 3 anime in common
            - one user's common ratings have no variation (denominator = 0)

        Preconditions:
            - self.kind == other.kind

        >>> g = WeightedGraph()
        >>> g.add_vertex("u1", "user")
        >>> g.add_vertex("u2", "user")
        >>> g.add_vertex("a1", "anime")
        >>> g.add_vertex("a2", "anime")
        >>> g.add_vertex("a3", "anime")
        >>> g.add_edge("u1", "a1", 5)
        >>> g.add_edge("u1", "a2", 4)
        >>> g.add_edge("u1", "a3", 1)
        >>> g.add_edge("u2", "a1", 3)
        >>> g.add_edge("u2", "a2", 2)
        >>> g.add_edge("u2", "a3", 1)
        >>> round(g.get_similarity_score("u1", "u2", "weighted"), 5)
        0.96077

        >>> g = WeightedGraph()
        >>> g.add_vertex("u1", "user")
        >>> g.add_vertex("u2", "user")
        >>> g.add_vertex("a1", "anime")
        >>> g.add_vertex("a2", "anime")
        >>> g.add_edge("u1", "a1", 5)
        >>> g.add_edge("u1", "a2", 4)
        >>> g.add_edge("u2", "a1", 3)
        >>> g.add_edge("u2", "a2", 2)
        >>> g.get_similarity_score("u1", "u2", "weighted")
        0.0
        """
        import math
        common_anime = set(self.neighbours.keys()).intersection(other.neighbours.keys())
        if len(common_anime) < 3:
            return 0.0
        self_scores = []
        other_scores = []
        for neighbour in common_anime:
            self_scores.append(self.neighbours[neighbour])
            other_scores.append(other.neighbours[neighbour])
        mean_self = sum(self_scores) / len(self_scores)
        mean_other = sum(other_scores) / len(other_scores)
        numerator = 0.0
        for i in range(len(self_scores)):
            numerator += (self_scores[i] - mean_self) * (other_scores[i] - mean_other)
        sum_sq_self = 0.0
        sum_sq_other = 0.0
        for i in range(len(self_scores)):
            sum_sq_self += (self_scores[i] - mean_self) ** 2
            sum_sq_other += (other_scores[i] - mean_other) ** 2
        denominator = math.sqrt(sum_sq_self) * math.sqrt(sum_sq_other)
        if denominator == 0:
            return 0.0
        return numerator / denominator


class WeightedGraph:
    """A graph used to represent a user rating - anime network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[str, _WeightedVertex]

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
            self._vertices[item] = _WeightedVertex(item, kind)

    def delete_vertex(self, item: str) -> None:
        """Delete a vertex with the given item from the graph"""
        if item in self._vertices:
            del self._vertices[item]

    def add_edge(self, item1: str, item2: str, weight: int = 1) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
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

        Note that the *items* are returned, not the _WeightedVertex objects themselves.

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

    def get_weight(self, item1: str, item2: str) -> int:
        """Return the weight of the edge between the given items.

        Return 0 if item1 and item2 are not adjacent.

        Preconditions:
            - item1 and item2 are vertices in this graph
        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.neighbours.get(v2, 0)

    def average_weight(self, item: str) -> float:
        """Return the average weight of the edges adjacent to the vertex corresponding to item.

        Raise ValueError if item does not corresponding to a vertex in the graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return sum(v.neighbours.values()) / len(v.neighbours)
        else:
            raise ValueError

    def get_similarity_score(self, item1: str, item2: str, score_type: str = "unweighted") -> float:
        """Return the similarity score between the two given items in this graph.

        score_type is one of 'unweighted' or 'strict', corresponding to the
        different ways of calculating weighted graph vertex similarity.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - score_type in {'unweighted', 'weighted'}

        >>> g = WeightedGraph()
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
        if item1 not in self._vertices or item2 not in self._vertices:
            raise ValueError
        if score_type == "unweighted":
            return self._vertices[item1].similarity_score_unweighted(self._vertices[item2])
        else:
            return self._vertices[item1].similarity_score_weighted(self._vertices[item2])

    def recommend_anime(self, inputted_ratings: dict[str, int], limit_users: int, score_type: str = "weighted") -> dict[str, int]:
        """Return a dictionary of up to <limit> recommended anime based on similarity to the given user based on the inputted
        list of anime titles. It takes the top anime from the top limit_users in similarity scores and then gives each one a
        new score by accumulating sim_score from user for every user that watched the anime.

        The return value is a dictionary mapping titles of anime to their similarity score

        The returned dictionary keys should NOT contain:
            - the input anime itself
            - any anime with a similarity score of 0 to the input anime
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
        for anime in inputted_ratings:
            self.add_edge("inputted_user", anime, inputted_ratings[anime])

        neighbour_users_to_score = []
        for user_id in self.get_all_vertices(kind='user'):
            sim_score = self.get_similarity_score(user_id, "inputted_user", "weighted")
            if sim_score > 0 and user_id != "inputted_user":
                neighbour_users_to_score.append((user_id, sim_score))
        neighbour_users_to_score.sort(key=lambda x: x[1], reverse=True)
        top_users = dict(neighbour_users_to_score[:limit_users])
        top_anime = set()
        for username in top_users:
            top_anime = top_anime.union(self.get_neighbours(username))
        anime_to_score = {}
        top_anime.difference_update(set(inputted_ratings.keys()))
        for anime in top_anime:
            total_score = 0
            total_similarity = 0
            for user in self.get_neighbours(anime):
                if user in top_users:
                    total_score += top_users[user] * self.get_weight(user, anime)
                    total_similarity += top_users[user]
            if total_similarity > 0:
                anime_to_score[anime] = round(total_score / total_similarity)
        return anime_to_score


def load_user_graph(user_file: str, anime_file: str) -> WeightedGraph:
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
    g = WeightedGraph()
    user_map = data_sanitization.clean_ratings(user_file)
    anime_map = data_sanitization.get_anime_id_title_map(anime_file, user_map)
    for user in user_map:
        g.add_vertex(user, "user")
        for anime, weight in user_map[user]:
            try:
                anime_title = anime_map[anime]
            except KeyError:
                continue
            g.add_vertex(anime_title, "anime")
            g.add_edge(user, anime_title, weight)

    return g


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['csv', 'networkx', 'data_sanitization'],
        'allowed-io': ['load_review_graph'],
        'max-nested-blocks': 4
    })
