def verify_match(bank_row, yardi_row):

    if abs(bank_row["amount"] - yardi_row["amount"]) > 0.01:
        return False

    date_diff = abs((bank_row["date"] - yardi_row["date"]).days)

    if date_diff > 3:
        return False

    return True