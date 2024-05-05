import sqlalchemy
from src.api import database as db

from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Retrieves the available catalog of games for people to purchase. 
    """
    catalog = []
    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("SELECT item_sku, name, publisher, price_in_cents, genre, platform, family_rating, mode_review FROM games")).fetchall()
        for game in results:
            catalog.append(
                {"sku": game.item_sku, 
                 "name": game.name, 
                 "publisher": game.publisher, 
                 "price": game.price_in_cents, 
                 "genre": game.genre, 
                 "platform": game.platform, 
                 "mode_review": game.mode_review,
                 "rating": game.family_rating})
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

