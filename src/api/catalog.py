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

@router.get("/catalog/trending/", tags=["catalog"])
def trending_catalog(time_unit: str = "day"):
    number_of_days = 0

    match time_unit:
        case "day": 
            number_of_days = 1
        case "week":
            number_of_days = 7
        case "month":
            number_of_days = 30
        case _:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Given unit of time is invalid or unsupported"
            )

    with db.engine.connect() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                with game_ids as (
                    select 
                        game_id,
                        sum(review) as recent_stars
                    from reviews
                    where review >= 4 and EXTRACT(EPOCH FROM (current_timestamp - created_at)) <= 3600 * 24 * :days
                    group by game_id
                    order by recent_stars
                    limit 5
                )
                select
                    item_sku, 
                    name, 
                    publisher, 
                    price_in_cents, 
                    genre, 
                    platform, 
                    family_rating,
                    release_date,
                    review
                from game_ids
                join games on game_ids.game_id = games.id
                join avg_review_view as rev_view on game_ids.game_id = rev_view.game_id
                """
            ),
            {"days": number_of_days}
        )

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


