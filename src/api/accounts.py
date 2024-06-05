import sqlalchemy
from src.api import database as db

from fastapi import APIRouter, Depends, HTTPException, status
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

@router.post("/register")
def register_customer(customer: Account):
    """Register's a customer with their name and email, returns their account_id"""
    with db.engine.begin() as connection:       
        try: 
            # try creating row in accounts table
            acc_id = connection.execute(
                sqlalchemy.text(
                    "INSERT INTO accounts (email, name) VALUES (:email, :name) returning id"
                ),
                {"name": customer.customer_name, "email": customer.customer_email}
            ).scalar_one()
            # account already exists (integrity error will occur when email unique across rows is broken, meaning account alr exists)
        except IntegrityError:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account with email already exists"
            )
        
    # returning account_id back so user can use it for rest of endpoints
    return {"account_id": acc_id}

@router.post("/{account_id}/view")
def account_view(account_id: int):
    """Using account_id, a customer can view their account to display purchased games, wishlisted games, and their current cart if it exists."""

    with db.engine.begin() as connection: 
        # retrieve the name corresponding to account_id
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
        # if name doesn't return anything, then raise 404 error saying account DNE
        if name is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account does not exist"
            )

        # passes account exists check
        # retrieves the games owned by that account
        games_owned = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.name
                FROM purchases
                JOIN games
                ON games.id = purchases.game_id
                WHERE purchases.account_id = :account_id
                """
            ),
            [{
                "account_id": account_id
            }]
        ).scalars()
        # list to hold games owned
        games = []
        for game in games_owned:
            games.append(game)
            # add to list one by one
        # retrieve wishlised games by that account
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
        ).scalars()
        wishlisted = []
        for game_w in wishlist:
            wishlisted.append(game_w)
        # fetch most recent cart they have (should only have one)
        games_in_cart = cost = 0
        try: 
            # try to fetch a cart
            current_cart_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT current_cart FROM accounts
                WHERE accounts.id = :account_id 
                """
            ),
             [{
                "account_id": account_id
            }]
            ).scalar_one()
            # if no cart found, then return the JSON response w the purchased/wishlisted games
        except NoResultFound:
            return {
            "customer_name": name,
            "games_owned": games,
            "wishlist": wishlisted,
            "current_cart": f"Games in cart: {games_in_cart}, Cost: {cost}"
        } 
        ## MAKE LESS REDUNDANT PLEASE 
        if not current_cart_id:
            return {
            "customer_name": name,
            "games_owned": games,
            "wishlist": wishlisted,
            "current_cart": f"Games in cart: {games_in_cart}, Cost: {cost}"
            }

        # Cart that's not checked out found, so get the count of games in cart and total cost
        cart_items_results = connection.execute(
            sqlalchemy.text(
                """
                SELECT total_games, total_cost
                FROM cart_values_view
                WHERE cart_id = :cart_id
                """
            ),
             [{
                "cart_id": current_cart_id
            }]
        ).fetchone()
        # unpack tuple
        games_in_cart, cost = cart_items_results
        # return json object w the data
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
    """Allows account to leave review on game."""

    with db.engine.begin() as connection:
        try:
            # try to find game that user wants to review
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
            # not found, means it doesn't exist in our inventory, throw 404 error w message
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game does not exist in inventory"
            )
        # game does exist in inventory, check to make sure the account has purchased the game
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
        # if account owns the game, then add their review into the reviews table. If that account has already reviewed it, then update their old review with the current
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
            # account does not own game, cannot review it
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cannot review a game you do not own."
            )
    # no exceptions raised, game successfully reviewed        
    return {
                "success": True,
                "msg": "Game successfully reviewed."
            }

class WishlistItem(BaseModel):
    sku: str

@router.post("/{account_id}/wishlist")
def add_to_wishlist(account_id: int, game: WishlistItem):
     """Allows account to wishlist game."""
     with db.engine.begin() as connection:
        # Integrity Error check
        try:
            # retreieve game ID for the game_sku passed
            game_id = connection.execute(
                sqlalchemy.text(
                    "SELECT id FROM games WHERE item_sku = :game_sku"
                ),
                [{
                    "game_sku": game.sku
                }]
            ).scalar_one()
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game does not exist in our inventory."
            )
        # flag for if the game has been purchased by the account
        already_purchased = (connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    COUNT(*)
                FROM purchases 
                WHERE 
                    account_id = :account_id AND game_id = :game_id
                """
            ),
            [{
                "account_id": account_id,
                "game_id": game_id
            }]
        ).scalar_one() > 0)
        # if they haven't purchased the game, add to the wishlisted table
        if not already_purchased:
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

                return {
                    "success": True
                }
            # have alr wishlisted, cannot wishlist again
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account already wishlisted this game")
        # have purchased, cannot wishlist game that they own
        else:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game has already been purchased by user")

@router.post("/{account_id}/wishlist/remove")
def remove_from_wishlist(account_id: int, game: WishlistItem):
    """Allows account to remove game from wishlist."""
    with db.engine.begin() as connection:
        # Integrity Error check
        try:
            # retreieve game ID for the game_sku passed
            game_id = connection.execute(
                sqlalchemy.text(
                    "SELECT id FROM games WHERE item_sku = :game_sku"
                ),
                [{
                    "game_sku": game.sku
                }]
            ).scalar_one()
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game does not exist in our inventory."
            )
        # flag for if the game has been purchased by the account
        removed_games = connection.execute(
            sqlalchemy.text(
                """
                DELETE 
                FROM wishlisted 
                WHERE 
                    account_id = :account_id AND game_id = :game_id
                RETURNING *
                """
            ),
            [{
                "account_id": account_id,
                "game_id": game_id
            }]
        ).fetchall()

        # if successful, return successful
        if removed_games:
            return {
                "success": True
            }
        # game not found in wishlist, cannot remove 
        else:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not in wishlist")
        

    
def format_game_recommendations(games):
    """helper function to format the json response for game recommendations"""
    res = []
    for game in games: 
        res.append(
            {
                "item_sku": game.item_sku,
                "name": game.name,
                "publisher": game.publisher,
                "price_in_cents": game.price_in_cents,
                "genre": game.genre,
                "platform": game.platform,
                "family_rating": game.family_rating,
                "release_date": game.release_date,
            }
        )
    return res

@router.post("/{account_id}/recommend")
def recommend_game(account_id: int):
    """Accounting for highly reviewed games, purchased games, and wishlisted games, recommend a specific account 5 games."""
    with db.engine.begin() as connection:
        # get games they reviewed highly
        reviews = connection.execute(
            sqlalchemy.text(
                """
                SELECT g.genre, g.publisher, g.platform, g.family_rating, g.id
                FROM reviews r 
                JOIN games g ON r.game_id = g.id
                WHERE r.account_id = :account_id AND r.review >= 3
                """
            ), {"account_id": account_id}
        ).fetchall()
        reviewed_games_id = {entry.id for entry in reviews}
        # get purchased games
        purchases = connection.execute(
            sqlalchemy.text(
                """
                SELECT g.genre, g.publisher, g.platform, g.family_rating, g.id
                FROM purchases p
                JOIN games g ON p.game_id = g.id
                WHERE p.account_id = :account_id AND g.id NOT IN :reviewed_game_ids
                """
            ),
            {"account_id": account_id, "reviewed_game_ids": tuple(reviewed_games_id)}
        ).fetchall()
        # if none purchased, use wishlisted
        wishlists = connection.execute(
            sqlalchemy.text(
                """
                SELECT g.genre, g.publisher, g.platform, g.family_rating, g.id
                FROM wishlisted w
                JOIN games g ON w.game_id = g.id
                WHERE w.account_id = :account_id
                """
            ),
            {"account_id": account_id}
        ).fetchall()

        #Game Ids to not exclude from recommendations
        exclude_game_ids = set()
        for entry in reviews + purchases + wishlists:
            exclude_game_ids.add(entry.id)

        # Calculate preferences based on the above data
        preferences = {"genre": {}, "publisher": {}, "platform": {}, "family_rating": {}}
        num_entries = 0

        def update_preferences(source, weight):
            nonlocal num_entries
            for entry in source:
                num_entries += 1
                # split the genres by , so "RPG, Fantasy" would become "RPG" and "Fantasy"
                genres = entry[0].split(", ")
                for genre in genres:
                    if genre not in preferences["genre"]:
                        # first encounter, init count to 0
                        preferences["genre"][genre] = 0
                    # add the weight to the counter for that genre
                    preferences["genre"][genre] += weight
                
                publisher = entry[1]
                if publisher not in preferences["publisher"]:
                    preferences["publisher"][publisher] = 0
                    # first encounter, init count to 0
                preferences["publisher"][publisher] += weight
                # add the weight to the counter for that publisher
                platform = entry[2]
                if platform not in preferences["platform"]:
                    preferences["platform"][platform] = 0
                    # first encounter, init count to 0
                preferences["platform"][platform] += weight
                # add the weight to the counter for that platform
                family_rating = entry[3]
                if family_rating not in preferences["family_rating"]:
                    preferences["family_rating"][family_rating] = 0
                    # first encounter, init count to 0
                preferences["family_rating"][family_rating] += weight
                # add the weight to the counter for that family rating
        
        # highly reviewed games carry most weight, then purchased, then wishlisted
        update_preferences(reviews, weight=3)
        update_preferences(purchases, weight=2)
        update_preferences(wishlists, weight=1)
        if num_entries == 0:
            # Recommend 5 random games if no data is available
            random_games_stmt = """
                SELECT item_sku, name, publisher, price_in_cents, genre, platform, family_rating, release_date
                FROM games
                WHERE id NOT IN :exclude_game_ids
                ORDER BY RANDOM()
                LIMIT 5
            """
            # exclude games that they already own or have wishlisted
            random_games = connection.execute(sqlalchemy.text(random_games_stmt), {"exclude_game_ids": tuple(exclude_game_ids)}).fetchall()
            return {"recommendations": format_game_recommendations(random_games)}
        
        for key in preferences:
            total = sum(preferences[key].values())
            for subkey in preferences[key]:
                preferences[key][subkey] /= total

         # Fetch all games
        all_games_stmt = """
            SELECT item_sku, name, publisher, price_in_cents, genre, platform, family_rating, release_date, id
            FROM games
            WHERE id NOT IN :exclude_game_ids
        """
        all_games = connection.execute(sqlalchemy.text(all_games_stmt), {"exclude_game_ids": tuple(exclude_game_ids)}).fetchall()
         # Calculate preference scores by adding them all together
        def calculate_preference_score(game):
            genre_score = sum(preferences["genre"].get(genre, 0) for genre in game.genre.split(", "))
            publisher_score = preferences["publisher"].get(game.publisher, 0)
            platform_score = preferences["platform"].get(game.platform, 0)
            family_rating_score = preferences["family_rating"].get(game.family_rating, 0)
            return genre_score + publisher_score + platform_score + family_rating_score

        # calculate pref score and then sort the games by score in descending order
        scored_games = [(game, calculate_preference_score(game)) for game in all_games]
        scored_games.sort(key=lambda x: x[1], reverse=True)
        
        # get the top 5 and return those
        top_games = [game[0] for game in scored_games[:5]]

        return format_game_recommendations(top_games)
