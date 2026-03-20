import pandas as pd
import os
import re

from app.utils.logger import get_logger, log_success, log_failure
import pdfplumber

logger = get_logger()


STANDARD_COLUMNS = [
    "date",
    "amount",
    "description",
    "reference"
]


# ---------- COLUMN DETECTION ----------
def _detect_columns(df):

    cols = {c.lower(): c for c in df.columns}

    mapping = {}

    for c in cols:

        if "date" in c:
            mapping["date"] = cols[c]

        elif "amount" in c or "amt" in c or "value" in c:
            mapping["amount"] = cols[c]

        elif "desc" in c or "narr" in c or "memo" in c:
            mapping["description"] = cols[c]

        elif "ref" in c or "cheque" in c or "txn" in c:
            mapping["reference"] = cols[c]

    return mapping


# ---------- NORMALIZATION ----------
def _normalize_df(df):

    mapping = _detect_columns(df)

    for std in STANDARD_COLUMNS:

        if std not in mapping:
            df[std] = None
        else:
            df[std] = df[mapping[std]]

    df = df[STANDARD_COLUMNS].copy()

    # DATE
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        dayfirst=True
    )

    # AMOUNT
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(",", "")
        .str.replace("CR", "")
        .str.replace("DR", "")
    )

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # DESCRIPTION
    df["description"] = (
        df["description"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # REFERENCE
    df["reference"] = (
        df["reference"]
        .astype(str)
        .str.lower()
        .str.replace(r"[^a-z0-9]", "", regex=True)
    )

    df = df.dropna(subset=["date", "amount"])

    df = df.reset_index(drop=True)

    return df


# ---------- CSV / TXT ----------
def _load_csv_like(path):

    try:

        df = pd.read_csv(path)

    except Exception:

        df = pd.read_csv(
            path,
            sep="|",
            engine="python"
        )

    return df


# ---------- XLSX ----------
def _load_excel(path):

    return pd.read_excel(path)


# ---------- BAI SIMPLE PARSER ----------
def _load_bai(path):

    rows = []

    with open(path, "r") as f:

        for line in f:

            parts = line.strip().split(",")

            if len(parts) < 3:
                continue

            try:

                rows.append({
                    "date": parts[1],
                    "amount": parts[2],
                    "description": parts[-1],
                    "reference": parts[0]
                })

            except Exception:
                continue

    return pd.DataFrame(rows)


# ---------- PDF BASIC ----------
def _load_pdf(path):

    try:
        import pdfplumber
    except:
        raise Exception("Install pdfplumber for PDF support")

    rows = []

    with pdfplumber.open(path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            for line in text.split("\n"):

                tokens = re.split(r"\s+", line)

                if len(tokens) < 3:
                    continue

                rows.append({
                    "date": tokens[0],
                    "amount": tokens[-1],
                    "description": " ".join(tokens[1:-1]),
                    "reference": ""
                })

    return pd.DataFrame(rows)


# ---------- MAIN ----------
def load_file(path):

    try:

        logger.info(f"Loading file: {path}")

        ext = os.path.splitext(path)[1].lower()

        if ext in [".csv", ".txt"]:
            df = _load_csv_like(path)

        elif ext in [".xlsx", ".xls"]:
            df = _load_excel(path)

        elif ext == ".bai":
            df = _load_bai(path)

        elif ext == ".pdf":
            df = _load_pdf(path)

        else:
            raise Exception(f"Unsupported file format: {ext}")

        df = _normalize_df(df)

        log_success(f"File loaded + normalized: {path}")

        print(f"Loaded {len(df)} normalized transactions")

        return df

    except Exception as e:

        log_failure(f"File loading failed: {path} | Error: {e}")
        raise