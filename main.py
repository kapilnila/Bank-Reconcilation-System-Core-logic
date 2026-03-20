from dotenv import load_dotenv
load_dotenv()

from app.pipeline.reconciliation_orchestrator import ReconciliationOrchestrator


if __name__ == "__main__":

    orchestrator = ReconciliationOrchestrator()

    result = orchestrator.run(
        "data/bank_statement.csv",
        "data/uploads/yardi_transactions.bai"
    )

    print("\n====== FINAL RECONCILIATION REPORT ======\n")

    for k, v in result.items():
        print(f"{k}: {v}")