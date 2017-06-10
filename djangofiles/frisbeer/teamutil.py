import itertools

from operator import itemgetter

def average(collection, key):
    return sum(key(item) for item in collection) / len(collection)


def form_teams(items, key=lambda x: x, n=3):
    """
    Generic function for partitioning a set of items into equal sized groups with
    close average value.
    :param items:   List of items to partition
    :param key:     Function defining what values are compared
    :param n:       Size of each partition. Sample size must be divisible by this.
    :return:
    """
    if len(items) % n != 0:
        raise ValueError("Player count is not divisible by {n}".format(n=n))
    elif len(items) % 2 != 0:
        raise ValueError("Player count is not divisible by 2")

    # Two teams
    if len(items) / n == 2:
        itemset = set(items)
        possibilities = itertools.combinations(itemset, n)
        scored_list = []
        for possibility in possibilities:
            team1 = possibility
            team2 = itemset - set(team1)
            score1 = average(team1, key)
            score2 = average(team2, key)
            scored_list.append((abs(score1 - score2), list(team1), list(team2)))
        ideal_teams = sorted(scored_list, key=itemgetter(0))[0]
        return [ideal_teams[1], ideal_teams[2]]
    else:
        halves = form_teams(items, key, n=n * 2)
        games = []
        for half in halves:
            teams = form_teams(half, key, n=n)
            games += teams
        return games