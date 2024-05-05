import sqlalchemy
from src.api import database as db

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    # with db.engine.begin() as connection:       
    #     connection.execute(
    #         sqlalchemy.text(
    #             "INSERT INTO accounts (email, name) VALUES (:name, :email)"
    #         ),
    #         {"name": customer.customer_name, "email": customer.customer_email}
    #     )

    return {"number_of_games": 0, "number_of_purchases": 0, "money": 0}
