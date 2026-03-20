from app.ingestion.file_manager import upload_and_normalize

path, df = upload_and_normalize(
    r"data/uploads/bank_statement.csv"
)

print(path)
print(len(df))