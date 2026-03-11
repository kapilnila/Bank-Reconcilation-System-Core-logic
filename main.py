from app.pipeline.reconciliation_pipeline import run_reconciliation


if __name__ == "__main__":

    result = run_reconciliation(
        "data/bank_statement.csv",
        "data/yardi_transactions.bai"
    )

    print("\n====== RECONCILIATION SUMMARY ======\n")

    for k, v in result.items():
        print(f"{k} : {v}")