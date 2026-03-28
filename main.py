"""
Run this file to run the entire program from start to finish
"""
import user_graph
import user_rating_graph
import attribute_graph

if __name__ == "__main__":
    # g = user_graph.load_user_graph("data/profiles.csv", "data/animes.csv")
    # print(g.get_all_vertices())
    # print(g.recommend_anime(['Haikyuu!! Second Season', 'Shigatsu wa Kimi no Uso', 'Made in Abyss', 'Fullmetal Alchemist: Brotherhood', 'Kizumonogatari III: Reiketsu-hen'], 20, 50))
    wg = user_rating_graph.load_user_graph("data/reviews_small.csv", "data/animes.csv")
    print(wg.get_weight("OVERPOWERED99", "One Punch Man"))
    print(wg.get_neighbours("One Punch Man"))
