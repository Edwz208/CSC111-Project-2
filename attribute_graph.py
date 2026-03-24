from __future__ import annotations
import csv
from typing import Any

import networkx as nx


class _Vertex:
    """A vertex in an anime show data graph, used to represent a show or an attribute.
    Each vertex item is either a show title or an attribute.
    Attributes will be:
    -uid
    -synopsis
    - genre
    - studio
    - popularity
    - episode count
    - score
    Both show title and attributes are represented as strings.

    Instance Attributes:
        - title: The data stored in this vertex representing a show, or an attribute.
        - kind: The type of this vertex: 'attribute' or 'show'.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'attribute', 'show'}
    """
    item: Any
    kind: str
    neighbours: set[_Vertex]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'attribute', 'show'}
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()

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
            - kind in {'show', 'attribute'}
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

    def load_review_graph(anime_data: str) -> Graph:
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

        >>> g = load_review_graph('data/reviews_small.csv', 'data/book_names.csv')
        >>> user1_reviews = g.get_neighbours('user1')
        >>> "Harry Potter and the Sorcerer's Stone (Book 1)" in user1_reviews
        True
        """

        show_attribute_graph = Graph()

        shows = {}

        with open(anime_data) as file:
            reader = csv.reader(file)
            for row in reader:
                uid = row[0]
                title = row[1]
                synopsis = row[2]
                genre = row[3]
                popularity = row[7]
                score = row[9]

                shows[uid] = title

                ## okay I just realized it doesn't make sense to write kind tags ad the name of the attribute
                ## I'm thinking about making a dictionary, I'll think about it.
                show_attribute_graph.add_vertex(synopsis, "synopsis")
                show_attribute_graph.add_vertex(genre, "genre")
                show_attribute_graph.add_vertex(popularity, "popularity")
                show_attribute_graph.add_vertex(score, "score")
                show_attribute_graph.add_edge(shows[uid], popularity)

        return show_attribute_graph
