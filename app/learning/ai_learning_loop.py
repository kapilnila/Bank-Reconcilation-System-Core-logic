from app.learning.mismatch_store import MismatchStore
from app.ai_services.rag_service import RagReconciliationService
from app.utils.logger import log_success, log_failure
import pandas as pd

class AILearningLoop:

    def __init__(self):

        try:

            self.store = MismatchStore()
            self.ai = RagReconciliationService()

            log_success("AI Learning Loop initialized")

        except Exception as e:

            log_failure(f"AI Learning Loop init failed: {e}")
            raise

    def process_unmatched(self, unmatched_bank, unmatched_yardi):

        try:

            total_cases = 0

            bank_data = unmatched_bank if isinstance(unmatched_bank, list) else unmatched_bank.to_dict("records")
            for bank_row in bank_data[:50]:

                query = f"""
                Bank transaction mismatch:

                amount: {bank_row['amount']}
                date: {bank_row['date']}
                description: {bank_row['description']}

                Suggest reconciliation reason.
                """

                explanation = self.ai.explain_reconciliation(query)

                text_case = f"""
                MISMATCH CASE

                Bank:
                {bank_row}

                AI Explanation:
                {explanation}
                """

                self.store.add_case(text_case)

                total_cases += 1

            self.store.save()

            log_success(f"AI learning processed {total_cases} cases")

        except Exception as e:

            log_failure(f"AI learning failed: {e}")