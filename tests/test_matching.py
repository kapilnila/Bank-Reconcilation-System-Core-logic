from app.matching.candidate_engine import CandidateEngine
from app.ingestion.loader import load_file
from app.normalization.normalize import normalize_transactions


yardi = normalize_transactions(
    load_file("data/yardi_transactions.bai"),
    "yardi"
)

engine = CandidateEngine(yardi)

bank_row = yardi.iloc[0]

cands = engine.generate(bank_row, 5)

print("Candidates:", len(cands))