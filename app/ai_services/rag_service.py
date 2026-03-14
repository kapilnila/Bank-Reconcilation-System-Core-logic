import os

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()

VECTOR_DB_PATH = "ai_memory"


class RagReconciliationService:

    def __init__(self):

        try:

            logger.info("Initializing RAG Service")

            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            # ---------- Load or Create Vector DB ----------
            if os.path.exists(VECTOR_DB_PATH):

                self.vector_store = FAISS.load_local(
                    VECTOR_DB_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )

                logger.info("Loaded existing vector DB")

            else:

                self.vector_store = FAISS.from_documents(
                    [],
                    self.embeddings
                )

                logger.info("Created new vector DB")

            # ---------- LLM ----------
            self.llm = ChatOpenAI(
                temperature=0
            )

            # ---------- QA Chain ----------
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 3}
                )
            )

            log_success("RAG Service initialized")

        except Exception as e:

            log_failure(f"RAG init failed: {e}")
            raise

    # ---------- Add New Knowledge ----------
    def add_memory(self, text):

        try:

            doc = Document(page_content=str(text))

            self.vector_store.add_documents([doc])

            log_success("Memory added to vector DB")

        except Exception as e:

            log_failure(f"Add memory failed: {e}")

    # ---------- Persist DB ----------
    def save_memory(self):

        try:

            self.vector_store.save_local(VECTOR_DB_PATH)

            log_success("Vector DB saved")

        except Exception as e:

            log_failure(f"Vector save failed: {e}")

    # ---------- Ask AI ----------
    def explain_reconciliation(self, query):

        try:

            logger.info("Running RAG query")

            result = self.qa_chain.run(query)

            return result

        except Exception as e:

            log_failure(f"RAG query failed: {e}")
            return "AI explanation unavailable"