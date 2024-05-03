import sqlalchemy
from src import database as db

from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    catalog = []
    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("SELECT sku, name, publisher, price, genre, platform, mode_review FROM TABLE_NAME_HERE_TBD"))
        for res in results:
            catalog.append({"sku": res.sku, "name": res.name, "publisher": res.publisher, "price": res.price, "genre": res.genre, "platform": res.platform, "mode_review": res.mode_review})
    return catalog

@router.get("/catalog/search/", tags=["catalog"])
def search_catalog():
    # Parameters?

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }

