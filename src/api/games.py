import sqlalchemy
import database as db

from fastapi import APIRouter, Depends
from pydantic import BaseModel
import auth

from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/games",
    tags=["games"],
    dependencies=[Depends(auth.get_api_key)],
)

# class Barrel(BaseModel):
#     sku: str

#     ml_per_barrel: int
#     potion_type: list[int]
#     price: int

#     quantity: int

@router.post("/{game_id}}/reviews")
def add_review(account_id: int, game_id: int, review: int):

    """ """
            
    return "OK"
