# Mission : corriger le bug FastAPI #15762

Tu travailles dans une copie de FastAPI 0.137.0 (le code d'avant la correction).
Ton seul travail : **proposer un correctif simple pour le bug ci-dessous, avec un test.**

## Le bug (issue #15762)

Titre : *0.137.0: empty-path route nested under prefix-less outer include raises 'Prefix and path cannot be both empty'*

```python
from fastapi import FastAPI, APIRouter

leaf = APIRouter()

@leaf.get("")                                # chemin vide
def list_items():
    return []

inner = APIRouter()
inner.include_router(leaf, prefix="/items")  # l'include intérieur A un préfixe

app = FastAPI()
app.include_router(inner)                     # l'include extérieur N'A PAS de préfixe
```

En 0.137.0, la dernière ligne lève :
`fastapi.exceptions.FastAPIError: Prefix and path cannot be both empty (path operation: list_items)`

En 0.136.3 et avant, le même code fonctionnait et enregistrait la route sur `/items`.

C'est une régression introduite par le refactor de l'arbre des routes (#15745), qui conserve les
instances `APIRouter`/`APIRoute` au lieu de les aplatir lors de l'include.

Le bug n'arrive que quand une route au chemin vide (`path=""`) est imbriquée **et** qu'au moins
un include de sa chaîne n'a pas de préfixe :

| cas | 0.136.3 | 0.137.0 |
|---|---|---|
| `app.include_router(leaf, prefix="/items")` (un seul include) | `/items` | marche |
| `inner` et `app` incluent tous deux avec un préfixe | `/v1/items` | marche |
| `inner` a un préfixe, `app.include_router(inner)` n'en a pas | `/items` | **plante** |

Piste donnée dans l'issue : dans `include_router` (`fastapi/routing.py`), quand `prefix` est vide,
le code parcourt les routes incluses et lève une erreur si le `path` **brut** d'une route est vide,
sans tenir compte des préfixes ajoutés par les routers intermédiaires.

## Ce que tu dois faire

1. Reproduire le bug : `uv run python repro_issue.py` (il plante tant que le bug est là).
2. Corriger le code dans `fastapi/` avec le **changement le plus petit et le plus simple possible**.
3. Ajouter un test qui échoue avant ta correction et passe après
   (par exemple dans `tests/test_empty_router.py`).
4. Vérifier :
   - `uv run python repro_issue.py` affiche `[]`
   - `uv run pytest tests/test_empty_router.py tests/test_router_include_context.py`
   - `uv run pytest tests -n auto` (le test `tests/test_fastapi_cli.py::test_fastapi_cli`
     échoue déjà avant ton changement, tu peux l'ignorer)
   - `uv run ruff check fastapi tests` et `uv run mypy fastapi/routing.py`
5. Résume ton correctif en quelques lignes : la cause, ce que tu as changé, les tests.

## Règles

- Ne fais **pas** de `git commit` ni de `git push` : la mise en ligne est gérée après toi.
- Ne cherche pas la solution officielle en ligne : c'est ta proposition qui compte.
- Ne modifie pas ce fichier, `repro_issue.py` ni `opencode.json`.
- Garde le style du code autour (noms, commentaires, typage).
