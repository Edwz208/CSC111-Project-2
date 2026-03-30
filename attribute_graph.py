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
    Both the show title and attributes are represented as strings.

    Instance Attributes:
        - title: The data stored in this vertex represents a show, or an attribute.
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

        >>> graph = Graph()
        >>> graph.add_vertex("Sailor Moon", "Title")
        >>> graph.add_vertex("Mahou Shoujo", "genre")
        >>> graph.add_edge("Sailor Moon", "Mahou Shoujo")
        >>> "Mahou Shoujo" in graph.get_neighbours("Sailor Moon")
        True

        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours items of the given item.

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


        >>> le_graph = Graph()
        >>> le_graph.add_vertex("Sailor Moon", "Title")
        >>> le_graph.add_vertex("Mahou Shoujo", "genre")
        >>> le_graph.add_vertex("Frieren", "Title")
        >>> le_graph.add_vertex("action", "genre")
        >>> le_graph.add_vertex("comedy", "genre")
        >>> le_graph.add_vertex("Mob Psycho", "Title")
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
        this is a helper function finding the show that has a similar name as the given input

        """
        input = show.lower().strip()
        all_shows = self.get_all_vertices(kind="title")

        for each_show in all_shows:
            if input in each_show.lower():
                return each_show
        return ""

    def recommend_new_show(self, shows: list[str], limit_anime: int) -> dict[str, float]:
        """
        this function returns a dict of recommended shows based on the similarity of the input show.
        Dictionary starts with the show that has the highest similarity, and does not exceed the given limit.

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
                    print(f" umm... We couldn't find '{show}', did you possibly mean {closest_title} ")
                else:
                    print(f" '{show}' is not found, so we couldn't find any match... "
                          f"but I prsonally recommend Frieren its a great anime !")

        all_shows = self.get_all_vertices(kind="title")
        for show in corrected_shows:
            if show in all_shows:
                all_shows.remove(show)
            elif show not in all_shows:
                closest_title = self.find_closes_title(show)
                all_shows.remove(closest_title)
                if closest_title == "":
                    pass

        scores_so_far = {}

        for the_show in all_shows:
            total_score = 0
            for show in corrected_shows:
                total_score += self.get_similarity_score(the_show, show)
            average = total_score/len(shows)
            if average > 0:
                scores_so_far[the_show] = average

        scores_so_far = sorted(scores_so_far.items(), key=lambda x: x[1], reverse=True)
        # scores_so_far.items() gave us all the key-value pairs as tuples
        # for each tuple, we care about x[1] which is the score
        # reverse=True -> highest value is first

        recommendation_dict = {}
        for title, score in scores_so_far[:limit_anime]:
            recommendation_dict[title] = score

        return recommendation_dict



def score_range_helper(score: float) -> str:
    """
    helper function that returns score
    :param score:
    :return:
    """
    if score >= 9.0:
        return "9-10"
    elif score >= 8.0:
        return "8-9"
    elif score >= 7.0:
        return "7-8"
    elif score >= 6.0:
        return "6-7"
    else:
        return "0-6"

def popularity_range_helper(popularity: float) -> str:
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
        next(reader)
        for row in reader:
            if len(row) >= 10 and row[9] != '':
                uid = row[0]
                title = row[1]
                genre = row[3].split(',')
                popularity = popularity_range_helper(float(row[7]))
                score = score_range_helper(float(row[9]))
                shows[uid] = title
                show_attribute_graph.add_vertex(title, "title")
                show_attribute_graph.add_vertex(popularity, "popularity")
                show_attribute_graph.add_vertex(score, "score")
                for singular_genre in genre:
                    singular_genre = singular_genre.strip()
                    show_attribute_graph.add_vertex(singular_genre, "genre")
                    show_attribute_graph.add_edge(title, singular_genre)

                show_attribute_graph.add_edge(title, popularity)
                show_attribute_graph.add_edge(title, score)

        return show_attribute_graph


if __name__ == '__main__':

    import doctest
    doctest.testmod()

if __name__ == '__main__':

    import doctest
    doctest.testmod()

    le_graph = load_the_graph('animes.csv')

    titles = list(le_graph.get_all_vertices(kind="title"))
    test_title = [titles[0], "narudo"]

    recommendations = le_graph.recommend_new_show(test_title, 30)

    if recommendations is None:
        print(f'Sorry you have a little bit too unique taste')
    else:
        index = 1
        print(f'Hello Hello dear user, since you liked "{test_title}" you might also like:')
        for title, score in recommendations.items():
            score_rounded = round(score, 2)
            print(f' {index}-) {title}, {score_rounded}')
            index += 1
