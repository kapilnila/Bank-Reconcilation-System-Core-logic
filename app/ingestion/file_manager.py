import os
import shutil
import uuid

from app.ingestion.loader import load_file
from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()

UPLOAD_DIR = "data/uploads"

ALLOWED_EXT = [
    ".csv",
    ".xlsx",
    ".xls",
    ".txt",
    ".bai",
    ".pdf"
]


def _safe_filename(original_path):

    ext = os.path.splitext(original_path)[1].lower()

    unique = uuid.uuid4().hex[:10]

    return f"txn_{unique}{ext}"


def upload_and_normalize(local_file_path):

    try:

        if not os.path.exists(local_file_path):
            raise Exception("File not found on local system")

        ext = os.path.splitext(local_file_path)[1].lower()

        if ext not in ALLOWED_EXT:
            raise Exception(f"Unsupported format: {ext}")

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        new_name = _safe_filename(local_file_path)

        dest_path = os.path.join(UPLOAD_DIR, new_name)

        shutil.copy(local_file_path, dest_path)

        logger.info(f"File uploaded to {dest_path}")

        df = load_file(dest_path)

        log_success(f"Upload + normalization completed: {new_name}")

        return dest_path, df

    except Exception as e:

        log_failure(f"Upload failed: {e}")
        raise