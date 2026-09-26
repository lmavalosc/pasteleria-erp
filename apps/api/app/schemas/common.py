from decimal import Decimal
from typing import Annotated
from pydantic import PlainSerializer

# Serializa Decimal como string de dos decimales (ej. "15000.00")
MoneyStr = Annotated[
    Decimal,
    PlainSerializer(lambda x: f"{x:.2f}", return_type=str, when_used="json"),
]
