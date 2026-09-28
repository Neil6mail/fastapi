"""Vérifie que la correction de l'issue #15762 ne casse pas les autres types de routes.

Chaque cas marchait avant la correction et doit continuer à marcher après.
Usage : uv run python regress_check.py
"""

from fastapi import APIRouter, FastAPI, WebSocket
from starlette.responses import PlainTextResponse
from starlette.routing import Route


def check(label, build):
    try:
        build()
        print("OK    ", label)
    except Exception as e:
        print("PLANTE", label, "->", type(e).__name__, e)


def nested_api_route():
    leaf = APIRouter()

    @leaf.get("/users")
    def read_users(): ...

    inner = APIRouter()
    inner.include_router(leaf, prefix="/v1")
    FastAPI().include_router(inner)


def nested_websocket():
    leaf = APIRouter()

    @leaf.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket): ...

    inner = APIRouter()
    inner.include_router(leaf, prefix="/v1")
    FastAPI().include_router(inner)


def nested_starlette_route():
    leaf = APIRouter()
    leaf.routes.append(Route("/hello", lambda request: PlainTextResponse("hi")))
    inner = APIRouter()
    inner.include_router(leaf, prefix="/v1")
    FastAPI().include_router(inner)


check("route GET /users imbriquée", nested_api_route)
check("websocket /ws imbriqué", nested_websocket)
check("route Starlette /hello imbriquée", nested_starlette_route)
