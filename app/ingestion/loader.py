import os
import re

import pandas as pd

from app.utils.logger import get_logger, log_success, log_failure


logger = get_logger()


# Output columns — every parser must produce exactly these
STANDARD_COLUMNS = ["date", "amount", "description", "reference"]


# ---------- COLUMN DETECTION ----------
# Maps whatever column names the source file uses → our standard names.
# Priority order matters: first match wins per standard column.
_COLUMN_HINTS = {
    "date": [
        "date", "txn_date", "transaction date", "posting date",
        "value date", "trans date", "effective date",
    ],
    "amount": [
        "amount", "amt", "value", "debit", "credit",
        "transaction amount", "net amount",
    ],
    "description": [
        "description", "desc", "narration", "narrative",
        "memo", "particulars", "details", "remarks",
    ],
    "reference": [
        "reference", "ref", "cheque", "check no", "check number",
        "txn id", "transaction id", "trans ref", "invoice",
    ],
}


def _detect_columns(df):
    """
    Returns a mapping { standard_name: actual_column_name }.
    Tries exact match first, then substring match.
    """
    cols_lower = {c.lower().strip(): c for c in df.columns}
    mapping = {}

    for std, hints in _COLUMN_HINTS.items():
        # exact match
        for hint in hints:
            if hint in cols_lower:
                mapping[std] = cols_lower[hint]
                break
        if std in mapping:
            continue
        # substring match
        for hint in hints:
            for col_lower, col_orig in cols_lower.items():
                if hint in col_lower:
                    mapping[std] = col_orig
                    break
            if std in mapping:
                break

    return mapping


# ---------- NORMALIZATION ----------
def _normalize_df(df):
    """
    Accepts a raw DataFrame from any parser.
    Returns a clean DataFrame with exactly STANDARD_COLUMNS,
    correct dtypes, and no rows missing date or amount.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    mapping = _detect_columns(df)

    # Build standard columns — use detected mapping or fill with None
    result = {}
    for std in STANDARD_COLUMNS:
        if std in mapping:
            result[std] = df[mapping[std]]
        elif std in df.columns:
            # column already named correctly (BAI parser output)
            result[std] = df[std]
        else:
            result[std] = None

    df = pd.DataFrame(result)

    # ── DATE ──────────────────────────────────────────────────────────────────
    # dayfirst=False so ISO dates (YYYY-MM-DD) are parsed correctly.
    # Timestamps (already datetime) pass through without re-parsing.
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)

    # ── AMOUNT ────────────────────────────────────────────────────────────────
    # Strip currency symbols, commas, CR/DR suffixes, then cast to float.
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(r"[£$€,]", "", regex=True)
        .str.replace(r"\s*(CR|cr)\s*$", "", regex=True)
        .str.replace(r"\s*(DR|dr)\s*$", "", regex=True)
        .str.strip()
    )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # ── DESCRIPTION ───────────────────────────────────────────────────────────
    df["description"] = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # ── REFERENCE ─────────────────────────────────────────────────────────────
    df["reference"] = (
        df["reference"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.replace(r"[^a-z0-9]", "", regex=True)
    )

    # ── DROP invalid rows ─────────────────────────────────────────────────────
    df = df.dropna(subset=["date", "amount"])
    df = df[df["amount"] != 0]
    df = df.reset_index(drop=True)

    return df[STANDARD_COLUMNS]


# ---------- CSV / TXT ----------
def _load_csv(path):
    """
    Tries comma delimiter first, then semicolon, then pipe.
    Handles BOM (utf-8-sig) that Excel sometimes adds.
    """
    for sep in [",", ";", "|"]:
        try:
            df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", dtype=str)
            if len(df.columns) >= 2:
                return df
        except Exception:
            continue

    raise ValueError(f"Could not parse CSV file: {path}")


# ---------- EXCEL ----------
def _load_excel(path):
    return pd.read_excel(path, dtype=str)


# ---------- BAI2 ----------
def _load_bai(path):
    """
    Stateful BAI2 parser.

    BAI2 key records:
      02  Group Header   → parts[4] = as_of_date (YYMMDD)
      03  Account ID     → parts[3] = as_of_date (YYMMDD) fallback
      16  Transaction    → parts[2]=amount (implied 2 decimals),
                           parts[4]=bank_ref, parts[5]=cust_ref,
                           parts[6+]=description
      88  Continuation   → appended to previous description

    Amounts use implied 2-decimal format: +267814 = $2,678.14
    """
    rows = []
    current_date = None
    last_row = None

    def _parse_bai_date(s):
        s = s.strip()
        if not s:
            return None
        try:
            return pd.to_datetime(s, format="%y%m%d")
        except Exception:
            return None

    def _parse_amount(s):
        s = s.strip().replace("+", "")
        negative = s.startswith("-")
        s = s.replace("-", "")
        amt = float(s) / 100.0
        return -amt if negative else amt

    with open(path, "r", errors="replace") as f:
        for raw_line in f:

            line = raw_line.strip().rstrip("/").strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split(",")]
            record_type = parts[0]

            # ── Group Header ─────────────────────────────────────────────────
            if record_type == "02" and len(parts) >= 5:
                d = _parse_bai_date(parts[4])
                if d is not None:
                    current_date = d

            # ── Account Identifier (fallback date source) ─────────────────────
            elif record_type == "03" and len(parts) >= 4:
                if current_date is None:
                    d = _parse_bai_date(parts[3])
                    if d is not None:
                        current_date = d

            # ── Transaction Detail ────────────────────────────────────────────
            elif record_type == "16" and len(parts) >= 3:
                try:
                    amount      = _parse_amount(parts[2])
                    bank_ref    = parts[4].strip() if len(parts) > 4 else ""
                    cust_ref    = parts[5].strip() if len(parts) > 5 else ""
                    reference   = bank_ref or cust_ref or ""
                    description = " ".join(parts[6:]).strip() if len(parts) > 6 else ""

                    last_row = {
                        "date":        current_date,
                        "amount":      amount,
                        "description": description,
                        "reference":   reference,
                    }
                    rows.append(last_row)

                except Exception as e:
                    log_failure(f"BAI2 type-16 parse failed: {line!r} | {e}")

            # ── Continuation record ───────────────────────────────────────────
            elif record_type == "88" and last_row is not None:
                extra = " ".join(parts[1:]).strip()
                if extra:
                    last_row["description"] = (
                        last_row["description"] + " " + extra
                    ).strip()

    if not rows:
        log_failure(f"BAI2 parser produced 0 rows from: {path}")

    return pd.DataFrame(rows)


# ---------- PDF ----------
def _load_pdf(path):
    """
    PDF bank statement parser using pdfplumber.

    Strategy:
      1. Try table extraction first — works for PDFs with visible table borders.
      2. Fall back to line-by-line text parsing for text-layout PDFs.

    Expected line format (text fallback):
      DD/MM/YYYY   DESCRIPTION TEXT   1,234.56
      YYYY-MM-DD   DESCRIPTION TEXT   -1,234.56
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "pdfplumber is required for PDF support. "
            "Run: pip install pdfplumber"
        )

    rows = []

    with pdfplumber.open(path) as pdf:

        for page in pdf.pages:

            # ── Strategy 1: table extraction ──────────────────────────────────
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                header = [
                    str(c).lower().strip() if c else ""
                    for c in table[0]
                ]
                has_header = any(
                    h in header
                    for h in ["date", "amount", "description", "balance"]
                )
                data_rows = table[1:] if has_header else table

                for row in data_rows:
                    if not row or all(
                        c is None or str(c).strip() == "" for c in row
                    ):
                        continue

                    cells = [str(c).strip() if c else "" for c in row]

                    if has_header and len(cells) == len(header):
                        row_dict = dict(zip(header, cells))
                    else:
                        row_dict = {
                            "date":        cells[0] if cells else "",
                            "amount":      cells[-1] if cells else "",
                            "description": " ".join(cells[1:-1]),
                            "reference":   "",
                        }

                    rows.append(row_dict)

            # ── Strategy 2: text line parsing ─────────────────────────────────
            if not tables:

                text = page.extract_text() or ""

                # Match lines that start with a date
                date_pattern = re.compile(
                    r"^(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"
                    r"|\d{4}[\/\-]\d{2}[\/\-]\d{2}"
                    r"|\d{1,2}[\-\s][A-Za-z]{3}[\-\s]\d{2,4})"
                )
                # Match amount at end of line (with optional sign)
                amount_pattern = re.compile(
                    r"([\-\+]?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*$"
                )

                for line in text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue

                    date_match   = date_pattern.match(line)
                    amount_match = amount_pattern.search(line)

                    if not date_match or not amount_match:
                        continue

                    date_str   = date_match.group(1)
                    amount_str = amount_match.group(1).replace(" ", "")
                    middle     = line[
                        len(date_str):amount_match.start()
                    ].strip()

                    # Extract a reference number from the description if present
                    ref_match = re.search(r"\b([A-Z0-9]{6,})\b", middle)
                    reference = ref_match.group(1) if ref_match else ""

                    rows.append({
                        "date":        date_str,
                        "amount":      amount_str,
                        "description": middle,
                        "reference":   reference,
                    })

    if not rows:
        log_failure(f"PDF parser produced 0 rows from: {path}")

    return pd.DataFrame(rows)


# ---------- MAIN ENTRY POINT ----------
def load_file(path):
    """
    Load any supported bank statement file.
    Returns a clean DataFrame with columns: date, amount, description, reference.

    Supported: .csv  .txt  .xlsx  .xls  .bai  .pdf
    """
    try:

        logger.info(f"Loading file: {path}")

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        ext = os.path.splitext(path)[1].lower()

        if ext in [".csv", ".txt"]:
            raw_df = _load_csv(path)

        elif ext in [".xlsx", ".xls"]:
            raw_df = _load_excel(path)

        elif ext == ".bai":
            raw_df = _load_bai(path)

        elif ext == ".pdf":
            raw_df = _load_pdf(path)

        else:
            raise ValueError(
                f"Unsupported file format: {ext}. "
                f"Supported: .csv .txt .xlsx .xls .bai .pdf"
            )

        df = _normalize_df(raw_df)

        if df.empty:
            log_failure(f"File loaded but produced 0 valid rows: {path}")
        else:
            log_success(f"File loaded: {path} → {len(df)} transactions")

        logger.info(f"Loaded {len(df)} normalized transactions")

        return df

    except Exception as e:
        log_failure(f"File loading failed: {path} | {e}")
        raise