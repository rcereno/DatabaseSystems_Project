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

class Account(BaseModel):
    customer_name: str
    customer_email: str

@router.post("/{customer_id}/register")
def register_customer(customer: Account):
    """ """
    try:
        with db.engine.begin() as connection:       
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO accounts (email, name) VALUES (:name, :email)"
                ),
                {"name": customer.customer_name, "email": customer.customer_email}
            )
    except IntegrityError:
        return {
            "success": False,
            "msg": "Account with email already exists"
        }
    
    return {
        "success": True,
        "msg": "Account successfully registered"
    }

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

