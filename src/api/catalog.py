import sqlalchemy
from src.api import database as db
from enum import Enum

from fastapi import APIRouter
metadata_obj = sqlalchemy.MetaData()
games = sqlalchemy.Table("games", metadata_obj, autoload_with=db.engine)
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


class search_sort_options(str, Enum):
    game_name = "name"
    price = "price"
    publisher = "publisher"
    platform = "platform"
    mode_review = "mode_review"
    genre = "genre"
    family_rating = "family_rating"
    release_date = "release_date"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"


@router.get("/catalog/search/", tags=["search"])
def search_catalog(
    game_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.release_date,
    sort_order: search_sort_order = search_sort_order.desc):

    query = (
            sqlalchemy.select(
                games.c.name,
                games.c.price_in_cents,
                games.c.publisher,
                games.c.platform,
                # NEED TO SOMEHOW ADD MODE REVIEW IN, NEED TO EDIT
                games.c.genre,
                games.c.family_rating,
                games.c.release_date
            ).select_from(games))
     
    with db.engine.begin() as connection:
        if game_sku:
            query = query.where(games.c.item_sku.ilike(f"{game_sku}"))
        if sort_col == search_sort_options.game_name:
            order_by = games.c.name
        elif sort_col == search_sort_options.price:
            order_by = games.c.price_in_cents
        elif sort_col == search_sort_options.publisher:
            order_by = games.c.publisher
        elif sort_col == search_sort_options.platform:
            order_by = games.c.platform
        elif sort_col == search_sort_options.mode_review:
            # EDIT THIS
            order_by = games.c.mode_review
        elif sort_col == search_sort_options.genre:
            order_by = games.c.genre
        elif sort_col == search_sort_options.family_rating:
            order_by = games.c.family_rating
        elif sort_col == search_sort_options.release_date:
            order_by = games.c.release_date
        else:
            order_by = games.c.release_date  # Default to release date if sort_col doesn't match any case

        if sort_order == search_sort_order.asc:
            query = query.order_by(order_by.asc())
        else:
            query = query.order_by(order_by.desc())
        
        if search_page:
            query = query.offset(int(search_page) * 5)

        results_db = connection.execute(query.limit(5))
        results = []
        prev = ""
        next_page = ""
        for row in results_db:
            print(row)
            results.append(
                {
                    "game_sku": row.name,
                    "price": row.price_in_cents,
                    "publisher": row.publisher,
                    "platform": row.platform,
                    "mode_review": 0,  # EDIT THIS
                    "genre": row.genre,
                    "family_rating": row.family_rating,
                    "release_date": row.release_date
                }
            )
        if search_page:
            prev = str(int(search_page) - 1) if int(search_page) > 0 else ""
            next_page = str(int(search_page) + 1) if len(results) >= 5 else ""
            if len(results) < 5:
                next_page = ""
        else:
            next_page =  "1" if len(results) >= 5 else ""
        response = {
            "previous": prev,
            "next": next_page,
            "results": results
        }
        return response


