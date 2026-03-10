import pandas as pd


def parse_yardi(path):

    df = pd.read_csv(path)

    df = df.rename(columns={
        "Amount": "amount",
        "Description": "description"
    })

    return df[["amount", "description"]]