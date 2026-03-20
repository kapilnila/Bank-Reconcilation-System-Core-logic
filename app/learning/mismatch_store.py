import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.utils.logger import log_success, log_failure


VECTOR_PATH = "ai_memory"


class MismatchStore:

    def __init__(self):

        try:

            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            if os.path.exists(VECTOR_PATH):

                self.vectordb = FAISS.load_local(
                    VECTOR_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )

            else:

                # FAISS requires at least one document to initialise the index.
                # This seed doc is never surfaced to the user.
                self.vectordb = FAISS.from_documents(
                    [Document(page_content="reconciliation mismatch store initialised")],
                    self.embeddings
                )

            log_success("MismatchStore initialized")

        except Exception as e:

            log_failure(f"MismatchStore init failed: {e}")
            raise

    def add_case(self, text):

        try:

            doc = Document(page_content=text)

            self.vectordb.add_documents([doc])

            log_success("Mismatch stored in vector memory")

        except Exception as e:

            log_failure(f"Mismatch store failed: {e}")

    def save(self):

        try:

            self.vectordb.save_local(VECTOR_PATH)

            log_success("Vector memory saved")

        except Exception as e:

            log_failure(f"Vector save failed: {e}")