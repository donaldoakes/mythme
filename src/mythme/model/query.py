from typing import Literal, get_args
from pydantic import BaseModel

Operator = Literal["=", ">", "<", ">=", "<=", "<>", "IN", "BETWEEN", "LIKE"]
operators = get_args(Operator)

Order = Literal["asc", "desc"]


class Sort(BaseModel):
    name: str
    order: Order = "asc"


class Paging(BaseModel):
    offset: int
    limit: int


class Criterion(BaseModel):
    name: str
    value: str
    operator: Operator = "="


class Query(BaseModel):
    criteria: list[Criterion]
    sort: Sort
    paging: Paging
    debug: bool = False


class SavedQuery(BaseModel):
    name: str
    criteria: list[Criterion]


class DbQuery(BaseModel):
    sql: str
    params: list[str]
