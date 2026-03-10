import pandas as pd


def parse_bai_file(file_path: str):

    transactions = []

    with open(file_path, "r") as f:

        for line in f:

            parts = line.strip().split(",")

            record_type = parts[0]

            if record_type == "16":

                transaction = {
                    "reference": parts[3],
                    "amount": float(parts[2]),
                    "description": parts[4] if len(parts) > 4 else "",
                }

                transactions.append(transaction)

    df = pd.DataFrame(transactions)

    return df