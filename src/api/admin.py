import sqlalchemy
from src.api import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

class Customer(BaseModel):
    account_id: int

@router.post("/reset")
def reset(
    cart_id: int,
    account_id = int
):
    """Resets entire shop"""
    with db.engine.begin() as connection:
        # Reset games table
        connection.execute(sqlalchemy.text("UPDATE games SET mode_review = NULL"))

        # Reset reviews table
        connection.execute(sqlalchemy.text("TRUNCATE reviews"))

        # Reset wishlisted table
        connection.execute(sqlalchemy.text("TRUNCATE wishlisted"))

        # Reset purchases table
        connection.execute(sqlalchemy.text("TRUNCATE purchases"))

        # Reset cart_items table
        connection.execute(sqlalchemy.text("TRUNCATE cart_items"))

        # Reset carts table
        connection.execute(sqlalchemy.text("TRUNCATE carts"))

        # Reset transactions table
        connection.execute(sqlalchemy.text("TRUNCATE transactions"))

    return "OK"

