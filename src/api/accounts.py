import sqlalchemy
from src import database as db

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


# if __name__ == "__main__":
#     list = get_bottle_plan()

#     notFirst = False

#     print("Potions made: ")
#     print("[")
#     for p in list:
#         potion_type = p["potion_type"]
#         quantity = p["quantity"]
#         if notFirst:
#             print(f",\n\t{potion_type}: {quantity}", end = '')
#         else:
#             print(f"\t{potion_type}: {quantity}", end = '')
#             notFirst = True
    
#     print("\n]")
