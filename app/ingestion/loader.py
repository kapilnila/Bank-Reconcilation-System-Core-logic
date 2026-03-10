import pandas as pd
from app.ingestion.bai_parser import parse_bai_file
from app.utils.logger import get_logger, log_success, log_failure

logger = get_logger()


def load_file(path: str) -> pd.DataFrame:

    try:

        logger.info(f"Loading file: {path}")

        # ---------- CSV ----------
        if path.endswith(".csv"):

            try:
                df = pd.read_csv(path)

            except Exception:

                df = pd.read_csv(path, delimiter=";")

            if len(df.columns) == 1:
                df = pd.read_csv(path, delimiter="|")

        # ---------- EXCEL ----------
        elif path.endswith(".xlsx") or path.endswith(".xls"):

            df = pd.read_excel(path)

        # ---------- TXT ----------
        elif path.endswith(".txt"):

            df = pd.read_csv(path, sep=None, engine="python")

        # ---------- BAI ----------
        elif path.endswith(".bai"):

            df = parse_bai_file(path)

        else:

            raise ValueError("Unsupported file format")

        log_success(f"File loaded successfully: {path}")

        print(f"Loaded {len(df)} transactions")

        return df

    except Exception as e:

        log_failure(f"File loading failed: {path} | Error: {str(e)}")

        raise