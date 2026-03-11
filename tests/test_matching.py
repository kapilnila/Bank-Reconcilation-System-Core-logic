from app.matching.hash_match import hash_match
from app.ingestion.loader import load_file
from app.normalization.normalize import normalize_transactions


bank = normalize_transactions(load_file("data/bank_statement.csv"), "bank")
yardi = normalize_transactions(load_file("data/yardi_transactions.bai"), "yardi")

result = hash_match(bank, yardi)

print("Matches:", len(result["matches"]))
print("Unmatched Bank:", len(result["unmatched_bank"]))
print("Unmatched Yardi:", len(result["unmatched_yardi"]))