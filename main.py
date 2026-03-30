"""
Run this file to run the entire program from start to finish
"""
import user_graph
import user_rating_graph
import attribute_graph


def combined_recommendation(user_recs: dict[str, float], attribute_recs: dict[str, float], returned_limit) -> list[str]:
    """
    Return a final list of anime titles based on the user-based recommendation and attribute-based recommendation and
    combining them. The final list has a chosen number returned.

    Up to <limit> anime are returned, starting with the anime with the highest similarity score,
    then the second-highest similarity score, etc. Fewer than <limit> anime are returned if
    and only if there aren't enough anime that meet the criteria.

    May need to normalize the scores to match up
    """
    COEFFICIENT = 0.5
    anime_final_score = {}
    for anime in user_recs:
        if anime in attribute_recs:
            combined_score = COEFFICIENT * user_recs[anime] + (1 - COEFFICIENT) * attribute_recs[anime]
            if combined_score > 0:
                anime_final_score[anime] = combined_score
    sorted_anime = sorted(anime_final_score.items(), key=lambda x: x[1], reverse=True)
    return [anime for anime, score in sorted_anime[:returned_limit]]


if __name__ == "__main__":

    # g = user_graph.load_user_graph("data/profiles.csv", "data/animes.csv")
    # print(g.recommend_anime(['Haikyuu!! Second Season', 'Shigatsu wa Kimi no Uso', 'Made in Abyss', 'Fullmetal Alchemist: Brotherhood', 'Kizumonogatari III: Reiketsu-hen'], 20, 50))
    wg = user_rating_graph.load_user_graph("data/reviews.csv", "data/animes.csv")
    print(wg.recommend_anime_weighted({"Fullmetal Alchemist: Brotherhood": 10, "Steins;Gate": 9, "Shingeki no Kyojin": 8, "Death Note": 7, "One Punch Man": 6 }, 100, 100))
