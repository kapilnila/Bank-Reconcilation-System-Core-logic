from app.matching.heuristic_hash_match import heuristic_hash_match
from app.ingestion.loader import load_file
from app.normalization.normalize import normalize_transactions


bank = normalize_transactions(load_file("data/bank_statement.csv"), "bank")
yardi = normalize_transactions(load_file("data/yardi_transactions.bai"), "yardi")

result = heuristic_hash_match(bank, yardi)

print("Heuristic Matches:", len(result["matches"]))