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
purchased = sqlalchemy.Table("purchases", metadata_obj, autoload_with=db.engine)


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

@router.get("/{cart_id}")
def cart_view(cart_id: int):
# Combine queries using joins to retrieve cart details, customer name, and game information
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    accounts.name AS customer_name,
                    carts.checked_out,
                    games.name AS game_name,
                    games.price_in_cents
                FROM carts
                JOIN accounts ON carts.account_id = accounts.id
                LEFT JOIN cart_items ON carts.id = cart_items.cart_id
                LEFT JOIN games ON cart_items.game_id = games.id
                WHERE carts.id = :cart_id
                """
            ),
            {"cart_id": cart_id}
        ).fetchall()

        if not result:
            return {"error": "Cart not found"}

        games_in_cart = []
        cost = 0
        customer_name = result[0].customer_name
        checked_out = result[0].checked_out
#Go through each row in the query result
# If the game name exists (not None), add it to the list of games in the cart
# Also, add the price of the game to the total cost
        for row in result:
            if row.game_name is not None:
                games_in_cart.append(row.game_name)
                cost += row.price_in_cents

    return {
        "cart_id": cart_id,
        "customer_name": customer_name,
        "games_in_cart": games_in_cart,
        "total_cost": cost,
        "checked_out": checked_out
    }


# class CartItem(BaseModel):
#     quantity: int

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str):
    """ """

    with db.engine.begin() as connection:
        try:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO cart_items (cart_id, game_id, cost)
                    SELECT :cart_id, id, price_in_cents
                    FROM games
                    WHERE item_sku = :item_sku
                    """
                ),
                {
                    "cart_id": cart_id,
                    "item_sku": item_sku
                }
            )

            connection.execute(sqlalchemy.text(
                """
                UPDATE carts 
                SET total_cost = total_cost + (
                    SELECT price_in_cents
                    FROM games
                    WHERE item_sku = :item_sku
                ),
                total_games = total_games + 1
                WHERE carts.id = :cart_id
                """
            ),
            {
                "item_sku": item_sku,
                "cart_id": cart_id
            })

        except IntegrityError:
            print("Game already in cart")
            return "OK"

    return {"success": True}


# class CartCheckout(BaseModel):
#     payment: str

@router.post("/{cart_id}/checkout")
# def checkout(cart_id: int, cart_checkout: CartCheckout):
def checkout(cart_id: int):
    """ """
    
    try:

        with db.engine.begin() as connection:
            # remove from wishlisted table if bought and they have it wishlisted
            connection.execute(
                    sqlalchemy.text(
                        """
                        with purchaser as (
                            select accounts.id 
                            from accounts
                            join carts
                                on accounts.id = carts.account_id
                            where carts.id = :cart_id
                        ),
                        cart_ids as (
                            select game_id from cart_items where cart_id = :cart_id
                        )
                        delete 
                        from wishlisted 
                        where 
                            wishlisted.game_id in (select game_id from cart_ids) and
                            wishlisted.account_id = (select id from purchaser)

                        """
                    ),
                    {
                        "cart_id": cart_id,

                    }
                    # sqlalchemy.delete(wishlisted)
                    # .where(wishlisted.c.game_id == cart_items.c.game_id)
                    # .where(cart_items.c.cart_id == cart_id)
                )
            
            ### UPDATED CART VALUES IN SET ITEM QUANTITY, NOT HERE
            # cart_items_results = connection.execute(
            #     sqlalchemy.text(
            #         """
            #         SELECT COUNT(game_id), SUM(cost)
            #         FROM cart_items
            #         WHERE cart_items.cart_id = :cart_id
            #         """
            #     ),
            #     [{
            #         "cart_id": cart_id
            #     }]
            # ).fetchone()
            # games_in_cart, cost = cart_items_results

            # Need to finish: updating cart amounts on checkout
            connection.execute(sqlalchemy.text(
                """
                UPDATE carts 
                SET checked_out = TRUE
                WHERE carts.id = :cart_id
                """
                ),
                [{
                    # "cost": cost,
                    # "game_count": games_in_cart,
                    "cart_id": cart_id
                }])
                    # removed from query
                    # total_cost = :cost, total_games = :game_count, 
            account_id = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT account_id FROM carts
                    WHERE carts.id = :cart_id
                    ORDER BY created_at DESC
                    """
                ),
                [{
                    "cart_id": cart_id
                }]
            ).scalar_one()
            games_bought = connection.execute(sqlalchemy.text(
                """
                SELECT game_id, cost
                FROM cart_items
                WHERE cart_items.cart_id = :cart_id
                """
            ),
            {"cart_id": cart_id}).fetchall()
            transaction_id = connection.execute(
                    sqlalchemy.text(
                            "INSERT INTO transactions (description) VALUES ('cart checkout for cart :id') RETURNING id"
                        ),
                        {"id": cart_id}
                ).scalar_one()
            to_purchase = []
            total_cost = 0
            for game_id, cost in games_bought:
                to_purchase.append(
                    {"account_id": account_id, "game_id": game_id, "transaction_id": transaction_id, "money_given": cost}
                )
                total_cost += cost
            connection.execute(
            sqlalchemy.insert(purchased),
                to_purchase,
            )

            games_in_cart, cost = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT total_games, total_cost
                    FROM carts
                    WHERE carts.id = :cart_id
                    """
                ),
                [{
                    "cart_id": cart_id
                }]
            ).fetchone()

    except IntegrityError:
        print("Cart already checked out")
        return {"games_bought": 0, "total_price": 0}



    #         # LEDGERIZING
    #     except IntegrityError as e:
    #         print("OMG THE CART CHECKOUT DIDN'T GO THROUGH")
    #         return {"total_potions_bought": 0, "total_gold_paid": 0}


        # for cart_items in results:



        # LEDGERIZING



    return {"games_bought": games_in_cart, "total_price": total_cost}
