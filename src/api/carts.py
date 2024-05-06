import sqlalchemy
from src.api import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

from sqlalchemy.exc import IntegrityError
metadata_obj = sqlalchemy.MetaData()
carts = sqlalchemy.Table("carts", metadata_obj, autoload_with=db.engine)
accounts = sqlalchemy.Table("accounts", metadata_obj, autoload_with=db.engine)
cart_items = sqlalchemy.Table("cart_items", metadata_obj, autoload_with=db.engine)
wishlisted = sqlalchemy.Table("wishlisted", metadata_obj, autoload_with=db.engine)

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class Customer(BaseModel):
    account_id: int

@router.post("/")
def create_cart(customer: Customer):
    """ """

    with db.engine.begin() as connection:

        cart_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO carts
                (account_id)
                VALUES 
                (:id)
                returning id
                """
            ),
            [{
                "id": customer.account_id
            }]
        ).scalar_one()

    return {"cart_id": cart_id}

@router.get("/{account_id}/{cart_id}")
def cart_view(account_id: int, cart_id: int):
    games_in_cart = []
    cost = 0
    with db.engine.begin() as connection:      
        game_resuls = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.name, games.price_in_cents 
                FROM games 
                JOIN cart_items ON games.id = cart_items.game_id
                WHERE cart_items.cart_id = :cart_id
                """
            ),
            [{
                "cart_id": cart_id
            }]
        ).fetchall()
        customer_name = connection.execute(
            sqlalchemy.text(
                """
                SELECT name 
                FROM accounts 
                JOIN carts ON carts.account_id = accounts.id
                """
            )).scalar_one()
        for game, price in game_resuls:
            games_in_cart.append(game)
            cost += price
    return {
        "cart_id": cart_id, 
        "customer_name": customer_name,
        "games_in_cart": games_in_cart,
        "total_cost": cost
    }


# class CartItem(BaseModel):
#     quantity: int

@router.post("/{cart_id}/items/{item_sku}")
# def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
def set_item_quantity(cart_id: int, item_sku: str):
    """ """

    with db.engine.begin() as connection:       
        gameId_price = connection.execute(
            sqlalchemy.text(
                "SELECT id, price_in_cents FROM games WHERE item_sku = :item_sku"
            ),
            {
                "item_sku": item_sku
            }).fetchone()
        try: 
            gameId, price = gameId_price
        except Exception:
            return "Game not available in inventory"
        connection.execute(
            sqlalchemy.text(
                "INSERT INTO cart_items (cart_id, game_id, cost) VALUES (:cart_id, :game_id, :cost)"
            ),
            [{
                "cart_id": cart_id,
                "game_id": gameId,
                "cost": price
            }]
        )

    return "OK"


# class CartCheckout(BaseModel):
#     payment: str

@router.post("/{cart_id}/checkout")
# def checkout(cart_id: int, cart_checkout: CartCheckout):
def checkout(cart_id: int):
    """ """
    
    with db.engine.begin() as connection:
        # remove from wishlisted table if bought and they have it wishlisted
        connection.execute(
                sqlalchemy.delete(wishlisted)
                .where(wishlisted.c.game_id == cart_items.c.game_id)
                .where(cart_items.c.cart_id == cart_id)
            )
        # Need to finish: updating cart amounts on checkout
        # connection.execute(sqlalchemy.text(
        #     """
        #     UPDATE carts 
        #     SET total_cost =  total_games = 

        #     """
        # ))
    #         # LEDGERIZING
    #         transaction_id = connection.execute(
    #             sqlalchemy.text(
    #                     "INSERT INTO transactions (type, description) VALUES ('cart checkout', 'did not set description yet') RETURNING id"
    #                 )
    #         ).scalar_one()
    #     except IntegrityError as e:
    #         print("OMG THE CART CHECKOUT DIDN'T GO THROUGH")
    #         return {"total_potions_bought": 0, "total_gold_paid": 0}


        # for cart_items in results:



        # LEDGERIZING



    return {"games_bought": 0, "total_price": 0}
