# Example Workflow
Example Flow 2: Add Game to Wishlist

User Story: As a gamer, I want to be able to wishlist games I 
want so that I can keep track of what I am interested in buying.

Scenario: Lyon Forester wants to add "GOLF IT" to his wishlist 
for future purchase.

Add to Wishlist
Endpoint: PUT /accounts/21/wishlist/golf_it_0




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

# Testing results

CURL STATEMENT
curl -X 'POST' \
  'https://redx-brri.onrender.com/accounts/21/wishlist/golf_it_0' \
  -H 'accept: application/json' \
  -H 'access_token: redx' \
  -d ''

RESPONSE
```
{
    "success": True
}
```

NOTE
wishlist table correctly updates with (account_id, game_id) = (21, 19)