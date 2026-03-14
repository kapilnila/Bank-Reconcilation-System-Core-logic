from app.ai_services.rag_service import RagReconciliationService

rag = RagReconciliationService()

print(
    rag.explain_reconciliation(
        "Bank transaction 500 amazon payment mismatch"
    )
)