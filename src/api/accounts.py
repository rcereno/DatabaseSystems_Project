import sqlalchemy
from src.api import database as db

from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/{customer_id}/register")
def register_customer( customer_id: int):
    """ """
    with db.engine.begin() as connection:       
        connection.execute(
            sqlalchemy.text(
                "INSERT INTO accounts (id, email, name) VALUES (:id, 'xia', 'testing')"
            ),
            {"id": customer_id}
        )
    
    return "OK"

@router.post("/{customer_id}/view")
def account_view():
    """
    """
        

    return {
        "customer_name": "",
        "games_owned": [],
        "wishlist": [],
        "current_cart": 0
    } 

