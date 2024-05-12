import sqlalchemy
from src.api import database as db

from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

from sqlalchemy.exc import NoResultFound
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

@router.post("/{account_id}/view")
def account_view(account_id: int):
    """
    """

    with db.engine.begin() as connection: 
        name = connection.execute(
            sqlalchemy.text(
                """
                SELECT name
                FROM accounts 
                WHERE id = :account_id
                LIMIT 1
                """
            ),
            [{
                "account_id": account_id
            }]
        ).scalar()

        games_owned = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.name
                FROM purchases
                JOIN games
                ON games.id = purchases.game_id
                WHERE purchases.account_id = :account_id
                ORDER BY play_time DESC
                """
            ),
            [{
                "account_id": account_id
            }]
        ).fetchall()
        games = []
        for game in games_owned:
            games.append(game)
        wishlist = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.name
                FROM wishlisted
                JOIN games
                ON games.id = wishlisted.game_id
                WHERE wishlisted.account_id = :account_id
                """
            ),
            [{
                "account_id": account_id
            }]
        ).fetchall()
        wishlisted = []
        for game_w in wishlist:
            wishlisted.append(game_w)
        # fetch most recent cart they have (should only have one)
        games_in_cart = cost = 0
        try: 
            current_cart_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM carts
                WHERE carts.account_id = :account_id AND carts.checked_out = FALSE
                ORDER BY created_at DESC
                """
            ),
             [{
                "account_id": account_id
            }]
            ).scalar_one()
        except NoResultFound:
            return {
            "customer_name": name,
            "games_owned": games,
            "wishlist": wishlisted,
            "current_cart": f"Games in cart: {games_in_cart}, Cost: {cost}"
        } 
        # Cart that's not checked out found, so do this
        cart_items_results = connection.execute(
            sqlalchemy.text(
                """
                SELECT COUNT(game_id), SUM(cost)
                FROM cart_items
                WHERE cart_items.cart_id = :cart_id
                """
            ),
             [{
                "cart_id": current_cart_id
            }]
        ).fetchone()
        games_in_cart, cost = cart_items_results

        return {
            "customer_name": name,
            "games_owned": games,
            "wishlist": wishlisted,
            "current_cart": f"Games in cart: {games_in_cart}, Cost: {cost}"
        } 

class Review(BaseModel):
    rating: int


@router.post("/{account_id}/reviews/{game_sku}")
def add_review(account_id: int, game_sku: str, review: Review):
    """ """

    with db.engine.begin() as connection:
        game_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM games 
                WHERE item_sku = :sku
                """
            ),
            [{
                "sku": game_sku
            }]
        ).scalar_one()
        purchased = connection.execute(
            sqlalchemy.text(
                """
                SELECT account_id, game_id
                FROM purchases
                WHERE account_id = :acc_id
                AND game_Id = :game_id
                """
            ),
            {
                "acc_id": account_id,
                "game_id": game_id
            }
        ).fetchone()
        if purchased:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO reviews (account_id, game_id, review)
                    VALUES (:account_id, :game_id, :review)
                    ON CONFLICT (account_id, game_id) DO UPDATE 
                    SET review = EXCLUDED.review
                    """
                ),
                [{
                    "account_id": account_id,
                    "game_id": game_id,
                    "review": review.rating
                }]
            )
        else:
            return "Cannot review a game you do not own."
            
    return "OK"


@router.post("/{account_id}/wishlist/{game_sku}")
def add_review(account_id: int, game_sku: str):
     with db.engine.begin() as connection:
        # Integrity Error check
        try:
            game_id = connection.execute(
                sqlalchemy.text(
                    "SELECT id FROM games WHERE item_sku = :game_sku"
                ),
                [{
                    "game_sku": game_sku
                }]
            ).scalar_one()
        except NoResultFound:
            return {
                "success": False,
                "msg": "This game does not exist in inventory."
            }
        try:
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO wishlisted (account_id, game_id) VALUES (:account_id, :game_id)"
                ),

                [{
                    "account_id": account_id,
                    "game_id": game_id
                }]

            )
        except IntegrityError as e:
            return {
                "success": False,
                "msg": "Account already wishlisted this game."
            }
        return {
                "success": True,
                "msg": "Game successfully added to wishlist."
            }
