import sqlalchemy
from src.api import database as db
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.api import auth

from sqlalchemy.exc import IntegrityError
# game_table = sqlalchemy.Table("games", metadata_obj, autoload_with=db.engine)

router = APIRouter(
    prefix="/games",
    tags=["games"],
    dependencies=[Depends(auth.get_api_key)],
)

# class with all the attributes we want to store in db
class Game(BaseModel):
    sku: str
    name: str
    publisher: str
    price: int
    platform: str
    genre: str
    family_rating: str
    release_date: datetime.date

@router.post("/add")
def add_to_game_inventory(games: list[Game]):
    """For shop keeper's use, add games to inventory."""
    games_to_add = []
    for game in games:
        # for each game given, add to our result
        games_to_add.append(
            {
                "item_sku": game.sku,
                "name": game.name,
                "publisher": game.publisher,
                "price_in_dollars": game.price,
                "platform": game.platform,
                "genre": game.genre,
                "family_rating": game.family_rating,
                "release_date": game.release_date
            }
        )
    with db.engine.begin() as connection:
        try: 
            # attempt to insert into games table
            connection.execute(
            sqlalchemy.insert(db.games),
                games_to_add,
            )
            # integrityError meaning game w/ sku alr exists
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game with sku already exists"
            )
    return "Games added"
