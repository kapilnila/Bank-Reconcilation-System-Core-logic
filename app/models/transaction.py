from pydantic import BaseModel
from datetime import datetime


class Transaction(BaseModel):

    transaction_id: str
    date: datetime
    amount: float
    description: str
    reference: str
    source: str