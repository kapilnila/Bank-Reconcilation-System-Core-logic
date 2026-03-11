from app.ingestion.loader import load_file
from app.normalization.normalize import normalize_transactions
from app.matching.exact_match import exact_match
from app.matching.hash_match import hash_match
from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()

HASH_THRESHOLD = 20000   # startup safe threshold


def run_reconciliation(bank_file, yardi_file):

    try:

        logger.info("Starting reconciliation pipeline")

        bank_df = load_file(bank_file)
        yardi_df = load_file(yardi_file)

        bank_df = normalize_transactions(bank_df, "bank")
        yardi_df = normalize_transactions(yardi_df, "yardi")

        bank_rows = len(bank_df)
        yardi_rows = len(yardi_df)

        logger.info(f"Bank rows={bank_rows} | Yardi rows={yardi_rows}")

        # ---------- ENGINE SELECTION ----------
        use_hash = max(bank_rows, yardi_rows) > HASH_THRESHOLD

        if use_hash:

            logger.info("Using HASH reconciliation engine")

            result = hash_match(bank_df, yardi_df)

        else:

            logger.info("Using MERGE reconciliation engine")

            matches = exact_match(bank_df, yardi_df)

            result = {
                "matches": matches.to_dict("records"),
                "unmatched_bank": [],
                "unmatched_yardi": []
            }

        log_success("Reconciliation completed")

        return {
            "engine_used": "hash" if use_hash else "merge",
            "bank_total": bank_rows,
            "yardi_total": yardi_rows,
            "match_count": len(result["matches"]),
            "unmatched_bank": len(result["unmatched_bank"]),
            "unmatched_yardi": len(result["unmatched_yardi"]),
            "matches_sample": result["matches"][:5]
        }

    except Exception as e:

        log_failure(f"Pipeline failed: {e}")

        # ---------- FAILSAFE FALLBACK ----------
        try:

            logger.info("Fallback → Trying merge engine")

            matches = exact_match(bank_df, yardi_df)

            return {
                "engine_used": "fallback_merge",
                "match_count": len(matches),
                "matches_sample": matches.head().to_dict("records")
            }

        except Exception as inner:

            log_failure(f"Fallback also failed: {inner}")

            raise