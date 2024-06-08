import sqlalchemy
from src.api import database as db
from enum import Enum

from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel
from src.api import auth
from enum import Enum

from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter
# metadata_obj = sqlalchemy.MetaData()
# games = sqlalchemy.Table("games", metadata_obj, autoload_with=db.engine)
router = APIRouter()

# metadata_obj = sqlalchemy.MetaData()
db.metadata_obj.reflect(bind=db.engine, views=True)
game_catalog = sqlalchemy.Table("game_catalog", db.metadata_obj, autoload_with=db.engine)


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Retrieves the available catalog of games for people to purchase. 
    """
    catalog = []
    try:
        with db.engine.begin() as connection:
            results = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT 
                        item_sku, 
                        name, 
                        publisher, 
                        price_in_dollars, 
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
                     "price": game.price_in_dollars, 
                     "genre": game.genre, 
                     "platform": game.platform, 
                     "avg_review": (game.review if game.review is not None else "NOT YET REVIEWED"),
                     "rating": game.family_rating,
                     "release_date": game.release_date})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return catalog

class search_sort_options(str, Enum):
    sku = "item_sku"
    game_name = "name"
    publisher = "publisher"
    price = "price"
    genre = "genre"
    # platform = "platform"
    avg_review = "review"
    release_date = "release_date"
    # family_rating = "family_rating"

class family_rating_options(str, Enum):
    E = "E"
    E10 = "E10"
    T = "T"
    M = "M"
    A0 = "A0"

class platform_options(str, Enum):
    PlayStation = "PlayStation"
    PC = "PC"
    Xbox = "Xbox"
    Nintendo = "Nintendo"

class review_options(int, Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   


@router.get("/catalog/search/", tags=["search"])
def search_catalog(
    game_sku: str = "",
    game_name: str = "",
    publisher: str = "",
    price: int = None,
    genre: str = "",
    platform: platform_options = None,
    review: review_options = None,
    rating: family_rating_options = None,
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.release_date,
    sort_order: search_sort_order = search_sort_order.desc):
    """Allows user to search our catalog with many search options/order."""
    # selecting all the attributes we want to return back to the user later
    query = (
            sqlalchemy.select(
                db.game_catalog.c.item_sku,
                db.game_catalog.c.name,
                db.game_catalog.c.price_in_dollars,
                db.game_catalog.c.publisher,
                db.game_catalog.c.platform,
                db.game_catalog.c.genre,
                db.game_catalog.c.family_rating,
                db.game_catalog.c.release_date,
                db.game_catalog.c.review
            ).select_from(db.game_catalog))
    with db.engine.begin() as connection:
        if game_sku != "":
            query = query.where(db.game_catalog.c.item_sku.ilike(f"%{game_sku}%"))
        if game_name != "":
            query = query.where(db.game_catalog.c.name.ilike(f"%{game_name}%"))
        if publisher != "":
            query = query.where(db.game_catalog.c.publisher.ilike(f"%{publisher}%"))
        if genre != "":
            query = query.where(db.game_catalog.c.genre.ilike(f"%{genre}%"))
        if platform:
            query = query.where(db.game_catalog.c.platform == platform)
        if rating:
            query = query.where(db.game_catalog.c.family_rating == rating)

        if price:
            if price  > 0  and price < 150:
                query = query.where(db.game_catalog.c.price_in_dollars <= price)
            elif price <= 0: #Don't run filter if 150 or above, error out if less than 0 
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Invalid price")
        
        if review:
            query = query.where((db.game_catalog.c.review >= review) if game_catalog.c.review != -1 else "NOT YET REVIEWED")

        # if review > 1 and review <= 5:
        #     query = query.where((db.game_catalog.c.review >= review) if game_catalog.c.review != -1 else "NOT YET REVIEWED")
        # elif review != 1: #Don't run sort filter if review is 1, error out otherwise
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Invalid review number")
                            
        # map sort options to corresponding column
        sort_columns = {
            search_sort_options.game_name: db.game_catalog.c.name,
            search_sort_options.sku: db.game_catalog.c.item_sku,
            search_sort_options.price: db.game_catalog.c.price_in_dollars,
            search_sort_options.publisher: db.game_catalog.c.publisher,
            search_sort_options.avg_review: db.game_catalog.c.review,  # EDIT THIS
            search_sort_options.genre: db.game_catalog.c.genre,
            search_sort_options.release_date: db.game_catalog.c.release_date,
        }
        # get column for sorting based on dictionary
        order_by = sort_columns.get(sort_col, db.game_catalog.c.release_date)
        # getting sort order
        if sort_order == search_sort_order.asc:
            query = query.order_by(order_by.asc())
        else:
            query = query.order_by(order_by.desc())
        
        # search page to paginate
        if search_page:
            query = query.offset(int(search_page) * 5)

        # run the query
        results_db = connection.execute(query.limit(5))
        results = []
        prev = ""
        next_page = ""
        # in the results from query, add each to results variable with the attributes
        for row in results_db:
            print(row)
            results.append(
                {
                    "game_sku": row.item_sku,
                    "name:": row.name,
                    "price": row.price_in_dollars,
                    "publisher": row.publisher,
                    "platform": row.platform,
                    "review": (row.review if row.review != -1 else "NOT YET REVIEWED"),  # EDIT THIS
                    "genre": row.genre,
                    "family_rating": row.family_rating,
                    "release_date": row.release_date
                }
            )
        # pagination
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

class time_unit(str, Enum):
    day = "day"
    week = "week"
    month = "month"

@router.get("/catalog/trending/", tags=["catalog"])
def trending_catalog(time_unit: time_unit = "day"):
    """Retrieves the recently trending games based on recent reviews."""
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
                    price_in_dollars, 
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
                 "price": game.price_in_dollars, 
                 "genre": game.genre, 
                 "platform": game.platform, 
                 "avg_review": (game.review if game.review != -1 else "NOT YET REVIEWED"),
                 "rating": game.family_rating,
                 "release_date": game.release_date})


        return json


