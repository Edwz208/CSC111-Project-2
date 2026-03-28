from __future__ import annotations
import csv
from typing import Any

import networkx as nx


class _Vertex:
    """A vertex in an anime show data graph, used to represent a show or an attribute.
    Each vertex item is either a show title or an attribute.
    Attributes will be:
    - genre
    - popularity
    - score
    Both show title and attributes are represented as strings.

    Instance Attributes:
        - title: The data stored in this vertex representing a show, or an attribute.
        - kind: The type of this vertex: 'attribute name' or 'show'.
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

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'title', 'genre', 'popularity', 'score'}
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()

    def similarity_score(self, other: _Vertex) -> float:
        """This function returns the similarity score between this and given vertex.
        """

        if not self.neighbours or not other.neighbours:
            return 0

        else:
            intersection_calc = self.neighbours.intersection(other.neighbours)
            union_calc = self.neighbours.union(other.neighbours)

            return len(intersection_calc) / len(union_calc)


class Graph:
    """A graph used to represent show-attribute relationship.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.
        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
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
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_attribute(self, i: int, anime_data: str) -> set:
        """
        this function will collect all the attributes in given index in a set.
        Raise a ValuError if index doesn't make sense.
                - uid = row[0]
                - title = row[1]
                - genre = row[3]
                - popularity = row[7]
                - score = row[9]
        """
        with open(anime_data) as file:
            reader = csv.reader(file)

            wanted = set()
            for row in reader:
                wanted.add(row[i])
            return wanted

    def get_all_vertices(self, kind: str = '') -> set:
        """The function will return a set of all vertex items of the given kind.

        Raise ValueError if kind is not given.

        Preconditions:
            - self.kind in {'title', 'genre', 'popularity', 'score'}
        """
        if kind == '':
            return set(self._vertices.keys())
        else:
            return {v.item for v in self._vertices.values() if v.kind == kind}

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.
        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        Note that this method is provided for you, and you shouldn't change it.
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
        if item1 not in self._vertices or item2 not in self._vertices:
            raise ValueError

        else:
            return self._vertices[item1].similarity_score(self._vertices[item2])

    def recommend_new_show(self, show: str) -> list[str]:
        """
        this function will be returning a list of recommended show based on the similarity of the input show

        The returned list should NOT contain:
            - the given show
            - any duplicates

        The returned list should contain:
            - list of shows with at least similarity score of 1


        The list will start with the book with the highest similarity score.

        Preconditions:
            - show in self._vertices
            - self._vertices[show].kind == 'title'
            - len(recommendation_list) => 1
        """

        all_shows = self.get_all_vertices(kind="title")
        all_shows.remove(show)

        scores_so_far = []

        for the_show in all_shows:
            score = self.get_similarity_score(the_show, show)
            if score > 0:
                scores_so_far.append((score, the_show))

        scores_so_far.sort(reverse=True)

        recommendation_list = []
        for score, title in scores_so_far:
            recommendation_list.append(title)

        return recommendation_list


def load_the_graph(anime_data: str) -> Graph:
    """Return a show-attribute relationship graph corresponding to the given datasets.
    Graph stores a vertex for each show and attributes in the datasets.
    Each vertex stores as its item either a show title or attributes.
    The show title vertices can not have an edge betwen them, nor can attribute vertices;
    A show vertex and an attribute vertex can have an edge between them.
    Use the "kind" _Vertex attribute to differentiate between different vertex types.
    Edges represent the relationship between a show and an attribute. In this graph, each edge
    only represents the existence of a relation.
    Preconditions:
        - anime_data is the path to a CSV file corresponding to the relevant anime data.
    """
    show_attribute_graph = Graph()
    shows = {}
    with open(anime_data) as file:
        reader = csv.reader(file)
        for row in reader:
            uid = row[0]
            title = row[1]
            genre = row[3]
            popularity = row[7]
            score = row[9]
            shows[uid] = title
            show_attribute_graph.add_vertex(title, "title")
            show_attribute_graph.add_vertex(genre, "genre")
            show_attribute_graph.add_vertex(popularity, "popularity")
            show_attribute_graph.add_vertex(score, "score")

            show_attribute_graph.add_edge(title, genre)
            show_attribute_graph.add_edge(title, popularity)
            show_attribute_graph.add_edge(title, score)

        return show_attribute_graph


