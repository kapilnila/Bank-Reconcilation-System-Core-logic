import pandas as pd
from collections import defaultdict
from rapidfuzz import fuzz

from app.utils.logger import get_logger, log_failure, log_success


logger = get_logger()

AMOUNT_TOLERANCE = 5.0
DATE_TOLERANCE_DAYS = 7
DESC_THRESHOLD = 45


def _ensure_df(data):

    """
    Production safety:
    Accept list / dataframe
    Always return dataframe
    """

    if isinstance(data, pd.DataFrame):
        return data

    if isinstance(data, list):
        if len(data) == 0:
            return pd.DataFrame()

        return pd.DataFrame(data)

    raise ValueError("Unsupported data type for matching")


def _confidence(bank_row, yardi_row):

    amount_diff = abs(bank_row["amount"] - yardi_row["amount"])
    date_diff = abs((bank_row["date"] - yardi_row["date"]).days)

    desc_score = max(
        fuzz.token_set_ratio(
            str(bank_row["description"]),
            str(yardi_row["description"])
        ),
        fuzz.partial_ratio(
            str(bank_row["description"]),
            str(yardi_row["description"])
        )
    )

    score = (
        max(0, 100 - (amount_diff * 10)) * 0.4 +
        max(0, 100 - (date_diff * 8)) * 0.3 +
        desc_score * 0.3
    )

    return round(score, 2)


def heuristic_hash_match(bank_df, yardi_df):

    try:

        logger.info("Starting HEURISTIC HASH reconciliation engine")

        bank_df = _ensure_df(bank_df)
        yardi_df = _ensure_df(yardi_df)

        if bank_df.empty or yardi_df.empty:

            return {
                "matches": [],
                "unmatched_bank": bank_df.to_dict("records"),
                "unmatched_yardi": yardi_df.to_dict("records")
            }

        yardi_buckets = defaultdict(list)

        # ---------- Build Buckets ----------
        for _, row in yardi_df.iterrows():
            bucket = round(float(row["amount"]))
            yardi_buckets[bucket].append(row)

        matches = []
        unmatched_bank = []

        # ---------- Matching ----------
        for _, bank_row in bank_df.iterrows():

            bucket = round(float(bank_row["amount"]))

            candidate_pool = []

            for b in range(bucket - 2, bucket + 3):
                candidate_pool.extend(yardi_buckets.get(b, []))

            best_candidate = None
            best_score = 0

            for yardi_row in candidate_pool:

                amount_diff = abs(
                    bank_row["amount"] - yardi_row["amount"]
                )

                if amount_diff > AMOUNT_TOLERANCE:
                    continue

                date_diff = abs(
                    (bank_row["date"] - yardi_row["date"]).days
                )

                if date_diff > DATE_TOLERANCE_DAYS:
                    continue

                desc_score = max(
                    fuzz.token_set_ratio(
                        str(bank_row["description"]),
                        str(yardi_row["description"])
                    ),
                    fuzz.partial_ratio(
                        str(bank_row["description"]),
                        str(yardi_row["description"])
                    )
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
                    "confidence": best_score
                })

                yardi_buckets[
                    round(float(best_candidate["amount"]))
                ].remove(best_candidate)

            else:
                unmatched_bank.append(bank_row)

        unmatched_yardi = []

        for remaining in yardi_buckets.values():
            unmatched_yardi.extend(remaining)

        log_success(
            f"HEURISTIC ENGINE COMPLETED | Matches={len(matches)}"
        )

        return {
            "matches": matches,
            "unmatched_bank": unmatched_bank,
            "unmatched_yardi": unmatched_yardi
        }

    except Exception as e:

        log_failure(f"Heuristic engine failed: {e}")
        raise