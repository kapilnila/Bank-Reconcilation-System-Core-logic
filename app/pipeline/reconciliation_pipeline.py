from app.ingestion.loader import load_file
from app.matching.exact_match import exact_match
from app.matching.fuzzy_match import fuzzy_match
from app.matching.heuristic_match import heuristic_match


def run_reconciliation(bank_file, yardi_file):

    bank_df = load_file(bank_file)
    yardi_df = load_file(yardi_file)

    exact = exact_match(bank_df, yardi_df)
    fuzzy = fuzzy_match(bank_df, yardi_df)
    heuristic = heuristic_match(bank_df, yardi_df)

    return {
        "exact_matches": exact,
        "fuzzy_matches": fuzzy,
        "heuristic_matches": heuristic
    }