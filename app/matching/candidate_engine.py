import bisect
from collections import defaultdict

from app.utils.logger import get_logger, log_failure


logger = get_logger()


class CandidateEngine:

    def __init__(self, yardi_df):

        try:

            self.amounts = []
            self.amount_rows = []

            self.token_index = defaultdict(list)

            for _, row in yardi_df.iterrows():

                amt = float(row["amount"])
                self.amounts.append(amt)
                self.amount_rows.append(row)

                tokens = str(row["description"]).lower().split()

                for t in tokens:
                    self.token_index[t].append(row)

            # sort by amount
            combined = sorted(zip(self.amounts, self.amount_rows), key=lambda x: x[0])

            self.amounts = [c[0] for c in combined]
            self.amount_rows = [c[1] for c in combined]

        except Exception as e:
            log_failure(f"CandidateEngine init failed: {e}")
            raise

    def amount_candidates(self, target_amount, tolerance):

        try:

            left = bisect.bisect_left(self.amounts, target_amount - tolerance)
            right = bisect.bisect_right(self.amounts, target_amount + tolerance)

            return self.amount_rows[left:right]

        except Exception as e:
            log_failure(f"Amount candidate search failed: {e}")
            return []

    def token_candidates(self, description):

        try:

            tokens = str(description).lower().split()

            candidate_set = set()

            for t in tokens:
                for row in self.token_index.get(t, []):
                    candidate_set.add(id(row))

            # recover rows
            results = []
            for row in self.amount_rows:
                if id(row) in candidate_set:
                    results.append(row)

            return results

        except Exception as e:
            log_failure(f"Token candidate search failed: {e}")
            return []

    def generate(self, bank_row, tolerance):

        try:

            amt_candidates = self.amount_candidates(
                float(bank_row["amount"]),
                tolerance
            )

            token_candidates = self.token_candidates(
                bank_row["description"]
            )

            # intersection logic
            token_ids = {id(r) for r in token_candidates}

            final = [
                r for r in amt_candidates
                if id(r) in token_ids
            ]

            return final if final else amt_candidates

        except Exception as e:
            log_failure(f"Candidate generation failed: {e}")
            return []