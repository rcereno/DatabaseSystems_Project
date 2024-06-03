import sqlalchemy
from src.api import database as db

from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel
from src.api import auth
from enum import Enum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound 



router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class Customer(BaseModel):
    account_id: int

@router.post("/")
def create_cart(customer: Customer):
    """Using account_id, create a cart for that account."""

    with db.engine.begin() as connection:
        # create new cart by inserting row into carts table
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
    # return user's cart id to then be used in later endpoints
    return {"cart_id": cart_id}

@router.get("/{cart_id}")
def cart_view(cart_id: int):
    with db.engine.begin() as connection:
        # Combine queries using joins to retrieve cart details, customer name, and game information
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

        # Go through each row in the query result
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

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str):
    """Add a specific game to a cart using cart_id."""

    with db.engine.begin() as connection:     
        try:   
            # retrieve game id and price from db
            gameId_price = connection.execute(
                sqlalchemy.text(
                    "SELECT id, price_in_cents FROM games WHERE item_sku = :item_sku"
                ),
                {
                    "item_sku": item_sku
                }).fetchone() 
            # game DNE in our inventory, raise http error
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not in inventory")
        # unpack tuple
        gameId, price = gameId_price
        try:
            # inserting row in cart items for the item added
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
            # updating the carts table with total games and price
            connection.execute(sqlalchemy.text(
                """
                UPDATE carts 
                SET total_cost = total_cost + :price, total_games = total_games + 1
                WHERE carts.id = :cart_id
                """
                ),
                [{
                    "price": price,
                    "cart_id": cart_id
                }])
        except IntegrityError:
            print("Game already in cart")
            return "OK"

    return {"success": True}

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """Checkout cart using cart_id."""
    
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
                )
            # set the cart checked_out value to be true
            connection.execute(sqlalchemy.text(
                """
                UPDATE carts 
                SET checked_out = TRUE
                WHERE carts.id = :cart_id
                """
                ),
                [{
                    "cart_id": cart_id
                }])
            # getting account id for this cart
            account_id = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT account_id FROM carts
                    WHERE carts.id = :cart_id
                    """
                ),
                [{
                    "cart_id": cart_id
                }]
            ).scalar_one()
            # getting games bought and costs from that cart
            games_bought = connection.execute(sqlalchemy.text(
                """
                SELECT game_id, cost
                FROM cart_items
                WHERE cart_items.cart_id = :cart_id
                """
            ),
            {"cart_id": cart_id}).fetchall()
            # track transaction in table
            transaction_id = connection.execute(
                    sqlalchemy.text(
                            "INSERT INTO transactions (description) VALUES ('cart checkout for cart :id') RETURNING id"
                        ),
                        {"id": cart_id}
                ).scalar_one()
            to_purchase = []
            total_cost = 0
            # making json object for each game bought in the cart
            for game_id, cost in games_bought:
                to_purchase.append(
                    {"account_id": account_id, "game_id": game_id, "transaction_id": transaction_id, "money_given": cost}
                )
                total_cost += cost
            # inserting into purchased table
            connection.execute(
            sqlalchemy.insert(db.purchased),
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

    return {"games_bought": games_in_cart, "total_price": total_cost}