from app.ingestion.loader import load_file
from app.normalization.normalize import normalize_transactions

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
            bank_df = normalize_transactions(
                load_file(bank_file),
                "bank"
            )

            yardi_df = normalize_transactions(
                load_file(yardi_file),
                "yardi"
            )

            total_bank = len(bank_df)
            total_yardi = len(yardi_df)

            # ---------- STAGE 1 EXACT ----------
            exact_df = exact_match(bank_df, yardi_df)

            matched_refs = set(exact_df["reference"])

            bank_remaining = bank_df[
                ~bank_df["reference"].isin(matched_refs)
            ]

            # ---------- STAGE 2 HASH ----------
            hash_result = hash_match(bank_remaining, yardi_df)

            hash_matches = hash_result["matches"]

            bank_remaining = hash_result["unmatched_bank"]
            yardi_remaining = hash_result["unmatched_yardi"]

            # ---------- STAGE 3 HEURISTIC ----------
            heuristic_result = heuristic_hash_match(
                bank_remaining,
                yardi_remaining
            )

            heuristic_matches = heuristic_result["matches"]

            bank_remaining = heuristic_result["unmatched_bank"]
            yardi_remaining = heuristic_result["unmatched_yardi"]

            # ---------- STAGE 4 AI SUGGESTIONS ----------
            candidate_engine = CandidateEngine(yardi_remaining)

            ai_suggestions = []

            for bank_row in bank_remaining[:50]:

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
                "total_bank": total_bank,
                "total_yardi": total_yardi,
                "exact_matches": len(exact_df),
                "hash_matches": len(hash_matches),
                "heuristic_matches": len(heuristic_matches),
                "remaining_unmatched_bank": len(bank_remaining),
                "remaining_unmatched_yardi": len(yardi_remaining),
                "ai_suggestions_generated": len(ai_suggestions)
            }

            log_success("Full reconciliation workflow completed")

            return report

        except Exception as e:

            log_failure(f"Orchestrator failed: {e}")

            raise