from app.pipeline.reconciliation_pipeline import run_reconciliation


if __name__ == "__main__":

    result = run_reconciliation(
        "data/bank_statement.csv",
        "data/yardi_transactions.bai"
    )

    print("Matches Found:")
    print(result["matches"])

    print("\nMissing Transactions:")
    print(result["missing"])