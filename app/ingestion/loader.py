import pandas as pd

def load_file(path):

    transactions = []

    with open(path, "r") as f:
        for line in f:

            line = line.strip()

            if not line:
                continue

            parts = line.split(",")

            record_type = parts[0]

            # Transaction detail
            if record_type == "16":

                try:
                    amount = parts[2]
                    description = parts[-1]

                    amount = int(amount.replace("+","").replace("-",""))

                    transactions.append({
                        "amount": amount,
                        "description": description.strip()
                    })

                except:
                    continue

    df = pd.DataFrame(transactions)

    print(f"Loaded {len(df)} transactions")

    return df