import os

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.utils.logger import log_success, log_failure


VECTOR_PATH = "ai_memory"


class MemoryStore:

    def __init__(self):

        try:

            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            if os.path.exists(VECTOR_PATH):

                self.vector_store = FAISS.load_local(
                    VECTOR_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )

            else:

                # FAISS needs at least one vector to determine embedding dimension
                self.vector_store = FAISS.from_documents(
                    [Document(page_content="reconciliation memory store initialised")],
                    self.embeddings
                )

            log_success("MemoryStore initialized")

        except Exception as e:

            log_failure(f"MemoryStore init failed: {e}")
            raise

    def add_reconciliation_case(self, text):

        try:

            doc = Document(page_content=text)

            self.vector_store.add_documents([doc])

            log_success("Reconciliation case added to AI memory")

        except Exception as e:

            log_failure(f"MemoryStore add failed: {e}")

    def save_memory(self):

        try:

            self.vector_store.save_local(VECTOR_PATH)

            log_success("AI memory saved")

        except Exception as e:

            log_failure(f"MemoryStore save failed: {e}")