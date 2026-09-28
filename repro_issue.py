from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

leaf = APIRouter()


@leaf.get("")
def list_items():
    return []


inner = APIRouter()
inner.include_router(leaf, prefix="/items")
app = FastAPI()
app.include_router(inner)
print(TestClient(app).get("/items").json())
