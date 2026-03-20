from app.ingestion.loader import load_file
from app.normalization.normalize import normalize_transactions
from app.matching.hash_match import _build_key

bank = normalize_transactions(
    load_file("data/bank_statement.csv"),
    "bank"
)

yardi = normalize_transactions(
    load_file("data/yardi_transactions.bai"),
    "yardi"
)

print("\nBANK SAMPLE\n")
print(bank.head(5))

print("\nYARDI SAMPLE\n")
print(yardi.head(5))

print("\nBANK COUNT:", len(bank))
print("YARDI COUNT:", len(yardi))
