import sqlalchemy
from src.api import database as db
import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

from sqlalchemy.exc import IntegrityError
metadata_obj = sqlalchemy.MetaData()
game_table = sqlalchemy.Table("games", metadata_obj, autoload_with=db.engine)

router = APIRouter(
    prefix="/games",
    tags=["games"],
    dependencies=[Depends(auth.get_api_key)],
)

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
    games_to_add = []
    for game in games:
        games_to_add.append(
            {
                "item_sku": game.sku,
                "name": game.name,
                "publisher": game.publisher,
                "price_in_cents": game.price,
                "platform": game.platform,
                "genre": game.genre,
                "family_rating": game.family_rating,
                "release_date": game.release_date
            }
        )
    with db.engine.begin() as connection:
        connection.execute(
        sqlalchemy.insert(game_table),
            games_to_add,
        )
    return "Game added"
