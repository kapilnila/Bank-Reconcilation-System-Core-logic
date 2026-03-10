import pandas as pd
from app.utils.logger import get_logger, log_failure, log_success

logger = get_logger()


def parse_bai_file(file_path: str):

    transactions = []

    try:

        with open(file_path, "r") as f:

            for line in f:

                parts = line.strip().split(",")

                if len(parts) == 0:
                    continue

                record_type = parts[0]

                if record_type == "16":

                    try:

                        transaction = {
                            "reference": parts[3] if len(parts) > 3 else None,
                            "amount": float(parts[2]) if len(parts) > 2 else 0,
                            "description": parts[4] if len(parts) > 4 else "",
                        }

                        transactions.append(transaction)

                    except Exception as row_error:

                        log_failure(
                            f"BAI row parsing failed: {line} | {row_error}"
                        )

        df = pd.DataFrame(transactions)

        log_success(f"BAI file parsed successfully: {file_path}")

        return df

    except Exception as e:

        log_failure(f"BAI parsing failed: {file_path} | Error: {str(e)}")

        raise