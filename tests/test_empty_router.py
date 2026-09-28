import pytest
from fastapi import APIRouter, FastAPI, WebSocket
from fastapi.exceptions import FastAPIError
from fastapi.testclient import TestClient

app = FastAPI()

router = APIRouter()


@router.get("")
def get_empty():
    return ["OK"]


app.include_router(router, prefix="/prefix")


client = TestClient(app)


def test_use_empty():
    with client:
        response = client.get("/prefix")
        assert response.status_code == 200, response.text
        assert response.json() == ["OK"]

        response = client.get("/prefix/")
        assert response.status_code == 200, response.text
        assert response.json() == ["OK"]


def test_include_empty():
    # if both include and router.path are empty - it should raise exception
    with pytest.raises(FastAPIError):
        app.include_router(router)


def test_empty_path_route_nested_under_prefixless_outer_include():
    """Empty-path route nested under prefix-less outer include should work.

    Regression test for FastAPI issue #15762.
    """
    leaf = APIRouter()

    @leaf.get("")
    def list_items():
        return []

    inner = APIRouter()
    inner.include_router(leaf, prefix="/items")

    app = FastAPI()
    app.include_router(inner)

    client = TestClient(app)
    resp = client.get("/items")
    assert resp.status_code == 200
    assert resp.json() == []


def test_empty_path_websocket_route_nested_under_prefixless_outer_include():
    """Empty-path websocket route nested under prefix-less outer include should work."""
    leaf = APIRouter()

    @leaf.websocket("")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_text("OK")
        await websocket.close()

    inner = APIRouter()
    inner.include_router(leaf, prefix="/ws")

    app = FastAPI()
    app.include_router(inner)

    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket_conn:
        assert websocket_conn.receive_text() == "OK"


def test_empty_path_starlette_route_nested_under_prefixless_outer_include():
    """Empty-path Starlette route nested under prefix-less outer include should work."""
    from starlette.responses import Response

    leaf = APIRouter()
    leaf.add_route("/", lambda _: Response("OK"))

    inner = APIRouter()
    inner.include_router(leaf, prefix="/hello")

    app = FastAPI()
    app.include_router(inner)

    client = TestClient(app)
    resp = client.get("/hello")
    assert resp.status_code == 200
    assert resp.text == "OK"


def test_empty_path_route_direct_include_still_rejects():
    """Empty path with no prefix at all should still raise."""
    leaf = APIRouter()

    @leaf.get("")
    def list_items():
        return []

    app = FastAPI()
    with pytest.raises(Exception, match="Prefix and path cannot be both empty"):
        app.include_router(leaf)


def test_empty_path_route_with_prefix():
    """Empty path with a prefix should work."""
    leaf = APIRouter()

    @leaf.get("")
    def list_items():
        return []

    app = FastAPI()
    app.include_router(leaf, prefix="/items")

    client = TestClient(app)
    resp = client.get("/items")
    assert resp.status_code == 200
    assert resp.json() == []


def test_nested_empty_path_with_multiple_prefixes():
    """Multiple levels of nesting with prefixes should work."""
    leaf = APIRouter()

    @leaf.get("")
    def list_items():
        return []

    inner = APIRouter()
    inner.include_router(leaf, prefix="/items")

    outer = APIRouter()
    outer.include_router(inner, prefix="/v1")

    app = FastAPI()
    app.include_router(outer)

    client = TestClient(app)
    resp = client.get("/v1/items")
    assert resp.status_code == 200
    assert resp.json() == []
