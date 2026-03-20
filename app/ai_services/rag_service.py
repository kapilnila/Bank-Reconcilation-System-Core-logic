import os

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()

VECTOR_DB_PATH = "ai_memory"


class RagReconciliationService:

    def __init__(self):

        logger.info("Initializing RAG Service")

        # ---------- EMBEDDINGS ----------
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # ---------- VECTOR DB ----------
        try:

            if os.path.exists(VECTOR_DB_PATH):

                self.vector_store = FAISS.load_local(
                    VECTOR_DB_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )

                logger.info("Loaded existing vector DB")

            else:

                self.vector_store = FAISS.from_texts(
                    ["initial reconciliation knowledge"],
                    self.embeddings
                )

                logger.info("Created new vector DB")

        except Exception as e:

            log_failure(f"Vector DB load failed: {e}")
            raise

        # ---------- OPTIONAL LLM ----------
        # RetrievalQA is imported lazily here to avoid the
        # langchain_core.pydantic_v1 crash when ENABLE_LLM=false
        self.qa_chain = None

        if os.getenv("ENABLE_LLM", "false").lower() == "true":

            try:

                from langchain.chains import RetrievalQA
                from langchain_openai import ChatOpenAI

                llm = ChatOpenAI(
                    temperature=0,
                    model="gpt-3.5-turbo"
                )

                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=self.vector_store.as_retriever(
                        search_kwargs={"k": 3}
                    )
                )

                log_success("LLM enabled")

            except Exception as llm_error:

                log_failure(f"LLM init failed: {llm_error}")

        log_success("RAG Service initialized")

    # ---------- MEMORY ----------
    def add_memory(self, text):

        try:
            self.vector_store.add_texts([str(text)])
            log_success("Memory added")

        except Exception as e:
            log_failure(f"Memory add failed: {e}")

    def save_memory(self):

        try:
            self.vector_store.save_local(VECTOR_DB_PATH)
            log_success("Vector DB saved")

        except Exception as e:
            log_failure(f"Vector save failed: {e}")

    # ---------- QUERY ----------
    def explain_reconciliation(self, query):

        try:

            if self.qa_chain is None:
                return "AI unavailable"

            return self.qa_chain.run(query)

        except Exception as e:

            log_failure(f"RAG query failed: {e}")
            return "AI explanation unavailable"
