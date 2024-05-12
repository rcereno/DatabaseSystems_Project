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
    #     
    with db.engine.begin() as connection:
        inventoryItems = connection.execute(sqlalchemy.text(
            '''SELECT 
                total_games, 
                total_purchases, 
                money 
                FROM total_inventory_view'''
            )
        ).one()
    print(f"number_of_games: {inventoryItems.total_games}, number_of_purchases: {inventoryItems.total_purchases}, money: {inventoryItems.money}")
    return {"number_of_games": inventoryItems.total_games, "number_of_purchases": inventoryItems.total_purchases, "money": inventoryItems.money}
