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


Example Flow 3: View Account Details

User Story: As a gamer, I want to be able to have my own account that 
keeps track of my owned games, wishlist, cart, billing (and other customer info).

Scenario: Mark wants to check the details of his account, including 
his owned games and items on his wishlist.


```
{
    "customer_name": "MarkD",
    "account_id": 789
}
```


RESPONSE


```
{
    "customer_name": "MarkD",
    "games_owned": ["Red Rawr Heros", "Am I Dead lol"],
    "wishlist": ["Gyat IV"],
    "current_cart": 102
}
```


Example Flow 4: Register Account / Purchase Games

User Story: As a gamer, I want to be able to create my own account so that I can purchase games.

Scenario: Eugene Fitzherbert wants to create an account and purchase two games.



curl -X 'POST' \
  'http://127.0.0.1:8000/accounts/{customer_id}/register' \
  -H 'accept: application/json' \
  -H 'access_token: redx' \
  -H 'Content-Type: application/json' \
  -d '{
  "customer_name": "Eugene Fitzherbert",
  "customer_email": "efitz13@gmail.com"
}'
```
{
    "customer_name": "Eugene Fitzherbert",
    "customer_email": "efitz13@gmail.com"
}
```


RESPONSE


```
{
    "customer_name": "MarkD",
    "games_owned": ["Red Rawr Heros", "Am I Dead lol"],
    "wishlist": ["Gyat IV"],
    "current_cart": 102
}
```







