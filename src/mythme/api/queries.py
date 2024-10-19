from fastapi import APIRouter, HTTPException
from mythme.model.query import SavedQuery
from mythme.data.queries import QueryData

router = APIRouter()


@router.get("/queries")
def get_queries() -> list[SavedQuery]:
    return QueryData().get_queries()


@router.get("/queries/{name}")
async def get_query(name: str) -> SavedQuery:
    query = QueryData().get_query(name)
    if query is None:
        raise HTTPException(status_code=404, detail=f"Query not found: {name}")
    return query


@router.post("/queries", status_code=201)
async def create_query(query: SavedQuery):
    query_data = QueryData()
    if query_data.get_query(query.name) is not None:
        raise HTTPException(
            status_code=409, detail=f"Query already exists: {query.name}"
        )
    query_data.save_query(query)
    return {"detail": "Created"}


@router.put("/queries/{name}")
async def update_query(name: str, query: SavedQuery):
    query_data = QueryData()
    if query_data.get_query(name) is None:
        raise HTTPException(status_code=404, detail=f"Query not found: {query.name}")
    if query.name != name:
        # renamed so delete old
        query_data.delete_query(name)
    query_data.save_query(query)
    return {"detail": "OK"}


@router.delete("/queries/{name}")
async def delete_query(name: str):
    query_data = QueryData()
    if query_data.get_query(name) is None:
        raise HTTPException(status_code=404, detail=f"Query not found: {name}")
    query_data.delete_query(name)
    return {"detail": "OK"}
