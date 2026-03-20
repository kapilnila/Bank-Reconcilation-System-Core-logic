import pandas as pd

from app.ingestion.loader import load_file

from app.matching.exact_match import exact_match
from app.matching.hash_match import hash_match
from app.matching.heuristic_hash_match import heuristic_hash_match
from app.matching.candidate_engine import CandidateEngine

from app.ai_services.ai_match_suggester import AIMatchSuggester
from app.learning.ai_learning_loop import AILearningLoop

from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()


class ReconciliationOrchestrator:

    def __init__(self):

        try:

            self.ai_suggester = AIMatchSuggester()
            self.learning_loop = AILearningLoop()

            log_success("ReconciliationOrchestrator initialized")

        except Exception as e:

            log_failure(f"Orchestrator init failed: {e}")
            raise

    def run(self, bank_file, yardi_file):

        try:

            logger.info("Starting FULL reconciliation workflow")

            # ---------- LOAD ----------
            # load_file already normalises internally — no second pass needed
            bank_df  = load_file(bank_file)
            yardi_df = load_file(yardi_file)

            total_bank  = len(bank_df)
            total_yardi = len(yardi_df)

            # ---------- STAGE 1 EXACT ----------
            exact_df = exact_match(bank_df, yardi_df)

            matched_bank_refs  = set(exact_df["reference"])
            matched_yardi_refs = set(exact_df["reference"])

            bank_remaining  = bank_df[
                ~bank_df["reference"].isin(matched_bank_refs)
            ].reset_index(drop=True)

            yardi_remaining = yardi_df[
                ~yardi_df["reference"].isin(matched_yardi_refs)
            ].reset_index(drop=True)

            # ---------- STAGE 2 HASH ----------
            hash_result = hash_match(bank_remaining, yardi_remaining)

            hash_matches = hash_result["matches"]

            # convert list → DataFrame for downstream stages
            bank_remaining  = pd.DataFrame(hash_result["unmatched_bank"])
            yardi_remaining = pd.DataFrame(hash_result["unmatched_yardi"])

            # ---------- STAGE 3 HEURISTIC ----------
            heuristic_result = heuristic_hash_match(
                bank_remaining,
                yardi_remaining
            )

            heuristic_matches = heuristic_result["matches"]

            bank_remaining  = pd.DataFrame(heuristic_result["unmatched_bank"])
            yardi_remaining = pd.DataFrame(heuristic_result["unmatched_yardi"])

            # ---------- STAGE 4 AI SUGGESTIONS ----------
            ai_suggestions = []

            if not yardi_remaining.empty and not bank_remaining.empty:

                candidate_engine = CandidateEngine(yardi_remaining)

                for _, bank_row in bank_remaining.head(50).iterrows():

                    candidates = candidate_engine.generate(
                        bank_row,
                        tolerance=5
                    )

                    suggestions = self.ai_suggester.suggest(
                        bank_row,
                        candidates
                    )

                    ai_suggestions.extend(suggestions)

            # ---------- STAGE 5 LEARNING ----------
            self.learning_loop.process_unmatched(
                bank_remaining,
                yardi_remaining
            )

            # ---------- FINAL REPORT ----------
            report = {
                "total_bank":               total_bank,
                "total_yardi":              total_yardi,
                "exact_matches":            len(exact_df),
                "hash_matches":             len(hash_matches),
                "heuristic_matches":        len(heuristic_matches),
                "remaining_unmatched_bank": len(bank_remaining),
                "remaining_unmatched_yardi":len(yardi_remaining),
                "ai_suggestions_generated": len(ai_suggestions)
            }

            log_success("Full reconciliation workflow completed")

            return report

        except Exception as e:

            log_failure(f"Orchestrator failed: {e}")
            raise