from collections import defaultdict
from rapidfuzz import fuzz
from datetime import timedelta

from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()


AMOUNT_TOLERANCE = 2.0      # configurable later
DATE_TOLERANCE_DAYS = 3
DESC_THRESHOLD = 65


def _amount_bucket(amount):
    """
    Bucket transactions by rounded amount for fast lookup
    """
    return round(float(amount))


def _confidence(bank_row, yardi_row):

    amount_diff = abs(bank_row["amount"] - yardi_row["amount"])

    date_diff = abs((bank_row["date"] - yardi_row["date"]).days)

    desc_score = fuzz.token_sort_ratio(
        str(bank_row["description"]),
        str(yardi_row["description"])
    )

    # weighted confidence
    score = (
        max(0, 100 - (amount_diff * 20)) * 0.4 +
        max(0, 100 - (date_diff * 15)) * 0.3 +
        desc_score * 0.3
    )

    return round(score, 2)


def heuristic_hash_match(bank_df, yardi_df):

    try:

        logger.info("Starting HEURISTIC HASH reconciliation engine")

        yardi_buckets = defaultdict(list)

        # ---------- Build Buckets ----------
        for _, row in yardi_df.iterrows():

            try:
                bucket = _amount_bucket(row["amount"])
                yardi_buckets[bucket].append(row)

            except Exception as e:
                log_failure(f"Bucket build failed: {e}")

        matches = []
        unmatched_bank = []

        # ---------- Matching ----------
        for _, bank_row in bank_df.iterrows():

            try:

                bucket = _amount_bucket(bank_row["amount"])

                candidate_pool = []

                # search nearby buckets
                for b in [bucket - 1, bucket, bucket + 1]:
                    candidate_pool.extend(yardi_buckets.get(b, []))

                best_candidate = None
                best_score = 0

                for yardi_row in candidate_pool:

                    amount_diff = abs(bank_row["amount"] - yardi_row["amount"])

                    if amount_diff > AMOUNT_TOLERANCE:
                        continue

                    date_diff = abs((bank_row["date"] - yardi_row["date"]).days)

                    if date_diff > DATE_TOLERANCE_DAYS:
                        continue

                    desc_score = fuzz.token_sort_ratio(
                        str(bank_row["description"]),
                        str(yardi_row["description"])
                    )

                    if desc_score < DESC_THRESHOLD:
                        continue

                    conf = _confidence(bank_row, yardi_row)

                    if conf > best_score:
                        best_score = conf
                        best_candidate = yardi_row

                if best_candidate is not None:

                    matches.append({
                        "bank_reference": bank_row["reference"],
                        "yardi_reference": best_candidate["reference"],
                        "amount_bank": bank_row["amount"],
                        "amount_yardi": best_candidate["amount"],
                        "date_bank": bank_row["date"],
                        "date_yardi": best_candidate["date"],
                        "confidence": best_score
                    })

                    # remove matched transaction
                    yardi_buckets[_amount_bucket(
                        best_candidate["amount"]
                    )].remove(best_candidate)

                else:
                    unmatched_bank.append(bank_row)

            except Exception as e:
                log_failure(f"Heuristic matching failed: {e}")

        unmatched_yardi = []
        for remaining in yardi_buckets.values():
            unmatched_yardi.extend(remaining)

        log_success(
            f"HEURISTIC ENGINE COMPLETED | Matches={len(matches)} | "
            f"UnmatchedBank={len(unmatched_bank)} | "
            f"UnmatchedYardi={len(unmatched_yardi)}"
        )

        return {
            "matches": matches,
            "unmatched_bank": unmatched_bank,
            "unmatched_yardi": unmatched_yardi
        }

    except Exception as e:

        log_failure(f"Heuristic engine failed: {e}")

        raise