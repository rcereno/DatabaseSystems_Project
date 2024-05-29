import sqlalchemy
from src.api import database as db
from enum import Enum

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter
metadata_obj = sqlalchemy.MetaData()
games = sqlalchemy.Table("games", metadata_obj, autoload_with=db.engine)
router = APIRouter()

metadata_obj = sqlalchemy.MetaData()
metadata_obj.reflect(bind=db.engine, views=True)
game_catalog = sqlalchemy.Table("game_catalog", metadata_obj, autoload_with=db.engine)


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Retrieves the available catalog of games for people to purchase. 
    """
    catalog = []
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    item_sku, 
                    name, 
                    publisher, 
                    price_in_cents, 
                    genre, platform, 
                    family_rating, 
                    review,
                    release_date
                FROM game_catalog
                """
            )
        ).fetchall()
        for game in results:
            catalog.append(
                {"sku": game.item_sku, 
                 "name": game.name, 
                 "publisher": game.publisher, 
                 "price": game.price_in_cents, 
                 "genre": game.genre, 
                 "platform": game.platform, 
                 "avg_review": (game.review if game.review is not None else "NOT YET REVIEWED"),
                 "rating": game.family_rating,
                 "release_date": game.release_date})
    return catalog





class search_sort_options(str, Enum):
    sku = "item_sku"
    game_name = "name"
    publisher = "publisher"
    price = "price"
    genre = "genre"
    platform = "platform"
    avg_review = "review"
    release_date = "release_date"
    rating = "family_rating"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/catalog/search/", tags=["catalog"])
def search_catalog(
    item_sku: str = "",
    game_name: str = "",
    publisher: str = "",
    price: int = 0,
    genre: str = "",
    platform: str = "",
    avg_review: int = 0,
    rating: str = "",
    sort_col: search_sort_options = search_sort_options.release_date,
    sort_order: search_sort_order = search_sort_order.desc,
):
    # Parameters?

    with db.engine.connect() as connection:        

        if sort_col is search_sort_options.sku:
            order_by = game_catalog.c.item_sku
        elif sort_col is search_sort_options.game_name:
            order_by = game_catalog.c.name
        elif sort_col is search_sort_options.publisher:
            order_by = game_catalog.c.publisher
        elif sort_col is search_sort_options.price:
            order_by = game_catalog.c.price_in_cents
        elif sort_col is search_sort_options.genre:
            order_by = game_catalog.c.genre
        elif sort_col is search_sort_options.platform:
            order_by = game_catalog.c.platform
        elif sort_col is search_sort_options.avg_review:
            order_by = game_catalog.c.review
        elif sort_col is search_sort_options.release_date:
            order_by = game_catalog.c.release_date
        elif sort_col is search_sort_options.rating:
            order_by = game_catalog.c.family_rating
        else: 
            assert False
        
        if sort_order is search_sort_order.desc:
            order_by = sqlalchemy.desc(order_by)

        sql = (
            sqlalchemy.select(
                game_catalog
            )
            .order_by(order_by)
        )

        if item_sku != "":
            sql = sql.where(game_catalog.c.item_sku.ilike(f"%{item_sku}%"))
        if game_name != "":
            sql = sql.where(game_catalog.c.name.ilike(f"%{game_name}%"))
        if publisher != "":
            sql = sql.where(game_catalog.c.publisher.ilike(f"%{publisher}%"))
        if genre != "":
            sql = sql.where(game_catalog.c.genre.ilike(f"%{genre}%"))
        if platform != "":
            sql = sql.where(game_catalog.c.platform.ilike(f"%{platform}%"))
        if rating != "":
            sql = sql.where(game_catalog.c.family_rating.ilike(f"%{game_name}%"))

        if price != 0 :
            sql = sql.where(game_catalog.c.price_in_cents <= price)

        if avg_review != 0:
            sql = sql.where((game_catalog.c.review >= avg_review) if game_catalog.c.review is not None else False)

        results = connection.execute(sql)
        json = []

        for game in results:
            json.append(
                {"sku": game.item_sku, 
                 "name": game.name, 
                 "publisher": game.publisher, 
                 "price": game.price_in_cents, 
                 "genre": game.genre, 
                 "platform": game.platform, 
                 "avg_review": (game.review if game.review != -1 else "NOT YET REVIEWED"),
                 "rating": game.family_rating,
                 "release_date": game.release_date})


    return json

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


