Example Flow 2: Add Game to Wishlist

User Story: As a gamer, I want to be able to wishlist games I 
want so that I can keep track of what I am interested in buying.

Scenario: Lisa wants to add "GAYT IV" to her wishlist 
for future purchase.

Add to Wishlist
Endpoint: PUT /21/wishlist/golf_it_0




```
{
   "account_id": 21,
   "game_sku": "golf_it_0"
}
```


RESPONSE
```
{
    "success": True
}
```