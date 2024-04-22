Example Flow 1: Search Games by Name

User Story: As a gamer, I want to be able to search games by 
name so that I can find a specific game quickly.

Scenario: Sam wants to find a game called "GAYT IV."

Search Games in Catalog
Endpoint: GET /catalog/search/
Query Parameters: game_name=GAYT IV
Action: Sam searches for "GAYT IV" using the game's name.



{
    "results": [
        
            "game_sku": "324334",
            "name": "GAYT IV",
            "price": 1,
            "publisher": "monster games",
            "platform": "PC",
            "mode_review": 5,
            "genre": "Fantasy",
            "release_date": "01/02/199"
        
    ]
}


Example Flow 2: Add Game to Wishlist

User Story: As a gamer, I want to be able to wishlist games I 
want so that I can keep track of what I am interested in buying.

Scenario: Lisa wants to add "GAYT IV" to her wishlist 
for future purchase.

Add to Wishlist
Endpoint: PUT /ET_LEG123/wishlist/456


{
    "customer_name": "LisaR",
    "account_id": 456
}

RESPONSE
{
    "success": true
}

Example Flow 3: View Account Details

User Story: As a gamer, I want to be able to have my own account that 
keeps track of my owned games, wishlist, cart, billing (and other customer info).

Scenario: Mark wants to check the details of his account, including 
his owned games and items on his wishlist.

{
    "customer_name": "MarkD",
    "account_id": 789
}
RESPONSE

{
    "customer_name": "MarkD",
    "games_owned": ["Red Rawr Heros", "Am I Dead lol"],
    "wishlist": ["Gayt IV"],
    "current_cart": 102
}







