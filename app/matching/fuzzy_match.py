from rapidfuzz import fuzz


def description_similarity(desc1: str, desc2: str):

    score = fuzz.ratio(desc1, desc2)

    return score


def fuzzy_match(desc1: str, desc2: str, threshold=80):

    score = description_similarity(desc1, desc2)

    return score >= threshold