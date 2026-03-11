from app.pipeline.reconciliation_pipeline import run_reconciliation


if __name__ == "__main__":

    result = run_reconciliation(
        "data/bank_statement.csv",
        "data/yardi_transactions.bai"
    )

    print("\n====== RECONCILIATION RESULT ======\n")

    print(f"Total Bank Transactions: {result['bank_total']}")
    print(f"Total Yardi Transactions: {result['yardi_total']}")
    print(f"Exact Matches Found: {len(result['matches'])}")

    print("\nSample Matches:\n")
    print(result["matches"].head())