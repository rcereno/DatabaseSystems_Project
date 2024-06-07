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

# class Cart(BaseModel):
#     id: int

# @router.get("/{account_id}")
# def cart_view(account_id: int, cart: Cart):
@router.get("/{account_id}/{cart_id}}")
def cart_view(account_id: int, cart_id: int):
    with db.engine.begin() as connection:
        # Combine queries using joins to retrieve cart details, customer name, and game information
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    accounts.id AS account_id,
                    accounts.name AS customer_name,
                    carts.checked_out,
                    games.name AS game_name,
                    games.price_in_dollars
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
            # return {"error": "Cart not found"}
        if result[0].account_id != account_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart view permission denied for user")

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
                # cost += row.price_in_dollars
        cost = connection.execute(sqlalchemy.text("""SELECT total_cost FROM cart_values_view WHERE cart_id = :cart_id"""),
                           {"cart_id": cart_id}).scalar_one()


    return {
        "cart_id": cart_id,
        "customer_name": customer_name,
        "games_in_cart": games_in_cart,
        "total_cost": cost,
        "checked_out": checked_out
    }

class CartItem(BaseModel):
    sku: str

@router.post("/{cart_id}/items")
def set_item_quantity(cart_id: int, item: CartItem):
    """ """

    with db.engine.begin() as connection:
        try:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO cart_items (cart_id, game_id, cost)
                    SELECT :cart_id, id, price_in_dollars
                    FROM games
                    WHERE item_sku = :item_sku
                    """
                ),
                {
                    "cart_id": cart_id,
                    "item_sku": item.sku
                }
            )

           
        except IntegrityError:
            print("Game already in cart")
            return "OK"

    return {"success": True}

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """ """
    
    try:
        with db.engine.begin() as connection:
            # Remove from wishlisted table if bought and they have it wishlisted
            connection.execute(
                sqlalchemy.text(
                    """
                    WITH purchaser AS (
                        SELECT accounts.id 
                        FROM accounts
                        JOIN carts ON accounts.id = carts.account_id
                        WHERE carts.id = :cart_id
                    ),
                    cart_ids AS (
                        SELECT game_id FROM cart_items WHERE cart_id = :cart_id
                    )
                    DELETE FROM wishlisted 
                    WHERE 
                        wishlisted.game_id IN (SELECT game_id FROM cart_ids) AND
                        wishlisted.account_id = (SELECT id FROM purchaser)
                    """
                ),
                {"cart_id": cart_id}
            )
            
            # Update cart status to checked out
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE carts 
                    SET checked_out = TRUE
                    WHERE id = :cart_id
                    """
                ),
                {"cart_id": cart_id}
            )
            
            # Retrieve account_id for the current cart
            account_id = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT account_id FROM carts
                    WHERE id = :cart_id
                    """
                ),
                {"cart_id": cart_id}
            ).scalar_one()
            
            # Retrieve games_bought and total_cost from the carts table
            cart_info = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT total_games, total_cost
                    FROM cart_values_view
                    WHERE cart_id = :cart_id
                    """
                ),
                {"cart_id": cart_id}
            ).fetchone()

            games_in_cart, total_cost = cart_info
            
            # Create a new transaction for the checkout
            transaction_id = connection.execute(
                sqlalchemy.text(
                    "INSERT INTO transactions (description) VALUES ('cart checkout for cart :id') RETURNING id"
                ),
                {"id": cart_id}
            ).scalar_one()
            
            # Insert purchased games into the purchases table
            games_bought = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO purchases (account_id, game_id, transaction_id, money_given)
                    SELECT :account_id, game_id, :transaction_id, cost
                    FROM cart_items
                    WHERE cart_id = :cart_id
                    RETURNING game_id
                    """
                ),
                {"account_id": account_id, "transaction_id": transaction_id, "cart_id": cart_id}
            ).fetchall()

    except IntegrityError:
        print("Cart already checked out")
        return {"games_bought": 0, "total_price": 0}

    return {"games_bought": games_in_cart, "total_price": total_cost}