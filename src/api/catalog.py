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
    platform = "platform"
    avg_review = "review"
    release_date = "release_date"
    family_rating = "family_rating"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   


@router.get("/catalog/search/", tags=["search"])
def search_catalog(
    game_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.release_date,
    sort_order: search_sort_order = search_sort_order.desc):
    """Allows user to search our catalog with many search options/order."""
    # selecting all the attributes we want to return back to the user later
    query = (
            sqlalchemy.select(
                db.games.c.item_sku,
                db.games.c.name,
                db.games.c.price_in_dollars,
                db.games.c.publisher,
                db.games.c.platform,
                db.games.c.genre,
                db.games.c.family_rating,
                db.games.c.release_date
            ).select_from(db.games))
    with db.engine.begin() as connection:
        if game_sku:
            query = query.where(db.games.c.item_sku.ilike(f"{game_sku}"))
        # map sort options to corresponding column
        sort_columns = {
            search_sort_options.game_name: db.games.c.name,
            search_sort_options.sku: db.games.c.item_sku,
            search_sort_options.price: db.games.c.price_in_dollars,
            search_sort_options.publisher: db.games.c.publisher,
            search_sort_options.platform: db.games.c.platform,
            # search_sort_options.mode_review: games.c.mode_review,  # EDIT THIS
            search_sort_options.genre: db.games.c.genre,
            search_sort_options.family_rating: db.games.c.family_rating,
            search_sort_options.release_date: db.games.c.release_date,
        }
        # get column for sorting based on dictionary
        order_by = sort_columns.get(sort_col, db.games.c.release_date)
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
                    "mode_review": 0,  # EDIT THIS
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

@router.get("/catalog/trending/", tags=["catalog"])
def trending_catalog(time_unit: str = "day"):
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


