from datetime import timedelta
from app.matching.fuzzy_match import fuzzy_match


def heuristic_match(bank_row, yardi_row):

    if bank_row["amount"] != yardi_row["amount"]:
        return False

    date_diff = abs((bank_row["date"] - yardi_row["date"]).days)

    if date_diff > 2:
        return False

    return fuzzy_match(
        bank_row["description"],
        yardi_row["description"]
    )