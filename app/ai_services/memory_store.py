from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.utils.logger import log_success

class MemoryStore:

    def __init__(self):

        self.embeddings = HuggingFaceEmbeddings()

        self.vector_store = FAISS.from_documents([], self.embeddings)

    def add_reconciliation_case(self, text):

        doc = Document(page_content=text)

        self.vector_store.add_documents([doc])

        log_success("Reconciliation case added to AI memory")

    def save_memory(self):

        self.vector_store.save_local("ai_memory")

        log_success("AI memory saved")