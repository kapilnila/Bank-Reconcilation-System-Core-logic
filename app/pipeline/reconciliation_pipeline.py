from app.ingestion.loader import load_file
from app.normalization.normalize import normalize_transactions
from app.matching.exact_match import exact_match


def run_reconciliation(bank_file, yardi_file):

    bank_df = load_file(bank_file)
    yardi_df = load_file(yardi_file)

    # normalize BEFORE matching
    bank_df = normalize_transactions(bank_df, "bank")
    yardi_df = normalize_transactions(yardi_df, "yardi")

    exact = exact_match(bank_df, yardi_df)

    return exact