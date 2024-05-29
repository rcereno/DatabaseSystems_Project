import sqlalchemy
from src.api import database as db

from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel
from src.api import auth
from enum import Enum

from sqlalchemy.exc import IntegrityError

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

