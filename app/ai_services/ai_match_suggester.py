from rapidfuzz import fuzz

from app.ai_services.rag_service import RagReconciliationService
from app.learning.mismatch_store import MismatchStore
from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()


class AIMatchSuggester:

    def __init__(self):

        try:

            self.ai = RagReconciliationService()
            self.memory = MismatchStore()

            log_success("AI Match Suggester initialized")

        except Exception as e:

            log_failure(f"AIMatchSuggester init failed: {e}")
            raise

    def _heuristic_score(self, bank_row, yardi_row):

        try:

            desc_score = fuzz.token_set_ratio(
                str(bank_row["description"]),
                str(yardi_row["description"])
            )

            amount_diff = abs(
                float(bank_row["amount"]) - float(yardi_row["amount"])
            )

            score = desc_score - (amount_diff * 5)

            return score

        except Exception as e:

            log_failure(f"Heuristic score failed: {e}")
            return 0

    def suggest(self, bank_row, candidates, top_k=3):

        try:

            if not candidates:
                return []

            scored = []

            for yardi_row in candidates:

                s = self._heuristic_score(bank_row, yardi_row)

                scored.append((s, yardi_row))

            scored.sort(reverse=True, key=lambda x: x[0])

            top_candidates = [c[1] for c in scored[:top_k]]

            # ---------- AI Ranking ----------
            suggestions = []

            for cand in top_candidates:

                try:

                    query = f"""
                    Bank transaction:

                    amount: {bank_row['amount']}
                    description: {bank_row['description']}

                    Candidate transaction:

                    amount: {cand['amount']}
                    description: {cand['description']}

                    Are these likely same transaction?
                    Give confidence 0-100 and reason.
                    """

                    ai_result = self.ai.explain_reconciliation(query)

                    suggestions.append({
                        "bank_ref": bank_row["reference"],
                        "yardi_ref": cand["reference"],
                        "ai_opinion": ai_result
                    })

                except Exception as inner:

                    log_failure(f"AI ranking failed: {inner}")

            log_success(f"AI suggestions generated: {len(suggestions)}")

            return suggestions

        except Exception as e:

            log_failure(f"Suggestion engine failed: {e}")
            return []