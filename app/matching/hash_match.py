from collections import defaultdict
from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()


def _build_key(row):
    """
    Stable reconciliation key
    """
    return (
        round(float(row["amount"]), 2),
        str(row["date"].date()),
        str(row["reference"]).strip()
    )


def hash_match(bank_df, yardi_df):

    try:

        logger.info("Starting HASH reconciliation engine")

        yardi_map = defaultdict(list)

        # ---------- Build Hash Index ----------
        for _, row in yardi_df.iterrows():

            try:
                key = _build_key(row)
                yardi_map[key].append(row)

            except Exception as e:
                log_failure(f"Yardi key build failed: {e}")

        matches = []
        unmatched_bank = []

        # ---------- Match Bank ----------
        for _, bank_row in bank_df.iterrows():

            try:
                key = _build_key(bank_row)

                if key in yardi_map and len(yardi_map[key]) > 0:

                    yardi_row = yardi_map[key].pop()

                    matches.append({
                        "bank_reference": bank_row["reference"],
                        "yardi_reference": yardi_row["reference"],
                        "amount": bank_row["amount"],
                        "date": bank_row["date"]
                    })

                else:
                    unmatched_bank.append(bank_row)

            except Exception as e:
                log_failure(f"Bank matching failed: {e}")

        # ---------- Remaining Unmatched Yardi ----------
        unmatched_yardi = []

        for remaining in yardi_map.values():
            unmatched_yardi.extend(remaining)

        log_success(
            f"HASH ENGINE COMPLETED | Matches={len(matches)} | "
            f"UnmatchedBank={len(unmatched_bank)} | "
            f"UnmatchedYardi={len(unmatched_yardi)}"
        )

        return {
            "matches": matches,
            "unmatched_bank": unmatched_bank,
            "unmatched_yardi": unmatched_yardi
        }

    except Exception as e:

        log_failure(f"Hash engine failed: {e}")

        raise