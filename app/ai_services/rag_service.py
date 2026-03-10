from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

from app.utils.logger import log_success, log_failure
class RagReconciliationService:

    def __init__(self):

        try:

            self.embeddings = HuggingFaceEmbeddings()

            self.vector_store = FAISS.load_local(
                "ai_memory",
                self.embeddings,
                allow_dangerous_deserialization=True
            )

            self.qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(),
                retriever=self.vector_store.as_retriever()
            )

            log_success("RAG service initialized")

        except Exception as e:

            log_failure(f"RAG service initialization failed: {str(e)}")

            raise

    def explain_reconciliation(self, query):

        try:

            result = self.qa_chain.run(query)

            return result

        except Exception as e:

            log_failure(f"RAG query failed: {str(e)}")

            return None