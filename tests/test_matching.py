from app.ai_services.rag_service import RagReconciliationService

rag = RagReconciliationService()

print(
    rag.explain_reconciliation(
        "Bank txn 500 amazon mismatch"
    )
)