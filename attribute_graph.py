from __future__ import annotations
import csv
from typing import Any

import networkx as nx


class _Vertex:
    """A vertex in an anime show data graph, used to represent a show or an attribute.
    Each vertex item is either a show title or an attribute.
    Attributes will be:
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
