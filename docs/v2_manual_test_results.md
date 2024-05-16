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

Scenario: Eugene Fitzherbert wants to check the details of his account, including 
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

REGISTER CUSTOMER
curl -X 'POST' \
  'https://redx-brri.onrender.com/accounts/%7Bcustomer_id%7D/register' \
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
"OK"
```

 NOTE 
 Eugene Fitzherbert is in account 23

 GET CATALOG
curl -X 'GET' \
  'https://redx-brri.onrender.com/catalog/' \
  -H 'accept: application/json'

RESPONCE

 ```
[
  {
    "sku": "it_takes_two_0",
    "name": "IT TAKES TWO",
    "publisher": "Hazelight Studios",
    "price": 21,
    "genre": "Co-op",
    "platform": "PC",
    "avg_review": NOT YET REVIEWED,
    "rating": "E10",
    "release_date": "2021-03-26"
  },
  {
    "sku": "apex_legends_0",
    "name": "APEX LEGENDS",
    "publisher": "Electronic Arts",
    "price": 0,
    "genre": "Shooter",
    "platform": "PC",
    "avg_review": -1,
    "rating": "T",
    "release_date": "2019-02-04"
  },
  {
    "sku": "witcher_3_wild_hunt_0",
    "name": "THE WITCHER 3: WILD HUNT",
    "publisher": "CD Projekt",
    "price": 60,
    "genre": "RPG",
    "platform": "PlayStation",
    "avg_review": -1,
    "rating": "M",
    "release_date": "2015-05-19"
  },
  {
    "sku": "spaghetti_western_simulator_0",
    "name": "SPAGHETTI WESTERN SIMULATOR",
    "publisher": "Al Dente Games",
    "price": 40,
    "genre": "Simulator",
    "platform": "PC",
    "avg_review": -1,
    "rating": "T",
    "release_date": "2023-09-15"
  },
  {
    "sku": "god_of_war_0",
    "name": "GOD OF WAR",
    "publisher": "Sony Interactive Entertainment",
    "price": 60,
    "genre": "Adventure",
    "platform": "PlayStation",
    "avg_review": -1,
    "rating": "M",
    "release_date": "2018-04-20"
  },
  {
    "sku": "gyat_iv_0",
    "name": "GYAT IV",
    "publisher": "Emans Recipes",
    "price": 100,
    "genre": "Adventure",
    "platform": "PC",
    "avg_review": -1,
    "rating": "A0",
    "release_date": "2023-07-18"
  },
  {
    "sku": "banana_bread_battle_0",
    "name": "BANANA BREAD BAKING BATTLE ROYALE",
    "publisher": "Yeast Entertainment",
    "price": 25,
    "genre": "Shooter",
    "platform": "Nintendo",
    "avg_review": -1,
    "rating": "E10",
    "release_date": "2024-03-14"
  },
  {
    "sku": "portal_0",
    "name": "PORTAL",
    "publisher": "Valve",
    "price": 13,
    "genre": "Puzzle",
    "platform": "PlayStation",
    "avg_review": -1,
    "rating": "E",
    "release_date": "2007-10-10"
  },
  {
    "sku": "call_of_duty_0",
    "name": "CALL OF DUTY",
    "publisher": "Activision",
    "price": 60,
    "genre": "Shooter",
    "platform": "Xbox",
    "avg_review": -1,
    "rating": "M",
    "release_date": "2009-11-10"
  },
  {
    "sku": "grandmas_farm_0",
    "name": "GRANDMAS FARM",
    "publisher": "Cursed Games Inc.",
    "price": 25,
    "genre": "Simulator",
    "platform": "PC",
    "avg_review": -1,
    "rating": "E",
    "release_date": "2024-04-01"
  },
  {
    "sku": "fallout_0",
    "name": "FALLOUT",
    "publisher": "Interplay Productions",
    "price": 50,
    "genre": "RPG",
    "platform": "PC",
    "avg_review": -1,
    "rating": "M",
    "release_date": "1997-09-30"
  },
  {
    "sku": "golf_it_0",
    "name": "GOLF IT",
    "publisher": "Perfuse Entertainment",
    "price": 10,
    "genre": "Party",
    "platform": "PC",
    "avg_review": -1,
    "rating": "E",
    "release_date": "2017-09-08"
  },
  {
    "sku": "overwatch_0",
    "name": "OVERWATCH",
    "publisher": "Blizzard Entertainment",
    "price": 40,
    "genre": "Shooter",
    "platform": "PC",
    "avg_review": -1,
    "rating": "T",
    "release_date": "2016-05-24"
  },
  {
    "sku": "loom_0",
    "name": "LOOM",
    "publisher": "Lucasfilm Games",
    "price": 3,
    "genre": "Adventure",
    "platform": "Nintendo",
    "avg_review": -1,
    "rating": "E",
    "release_date": "1990-04-29"
  },
  {
    "sku": "hairy_pickles_squirrel_0",
    "name": "HAIRY PICKLES VS. THE SQUIRREL ARMADA",
    "publisher": "Nutty Entertainment",
    "price": 15,
    "genre": "Shooter",
    "platform": "Xbox",
    "avg_review": -1,
    "rating": "E10",
    "release_date": "2024-06-30"
  },
  {
    "sku": "monkey_island_0",
    "name": "THE SECRET OF MONKEY ISLAND",
    "publisher": "Emans Recipes",
    "price": 5,
    "genre": "Adventure",
    "platform": "Xbox",
    "avg_review": -1,
    "rating": "M",
    "release_date": "1990-11-02"
  },
  {
    "sku": "overcooked_0",
    "name": "OVERCOOKED",
    "publisher": "Ghost Town Games",
    "price": 22,
    "genre": "Co-op",
    "platform": "PlayStation",
    "avg_review": -1,
    "rating": "E",
    "release_date": "2024-05-10"
  },
  {
    "sku": "grounded_0",
    "name": "GROUNDED",
    "publisher": "Obsidian Entertainment",
    "price": 40,
    "genre": "Adventure",
    "platform": "PC",
    "avg_review": -1,
    "rating": "E10",
    "release_date": "2020-07-28"
  },
  {
    "sku": "hatred_0",
    "name": "HATRED",
    "publisher": "Destructive Creations",
    "price": 20,
    "genre": "Shooter",
    "platform": "PC",
    "avg_review": -1,
    "rating": "A0",
    "release_date": "2015-06-01"
  },
  {
    "sku": "animal_crossing_new_horizons_0",
    "name": "ANIMAL CROSSING: NEW HORIZONS",
    "publisher": "Nintendo",
    "price": 60,
    "genre": "Simulator",
    "platform": "Nintendo",
    "avg_review": -1,
    "rating": "E",
    "release_date": "2020-03-20"
  },
  {
    "sku": "theme_park_0",
    "name": "THEME PARK",
    "publisher": "Electronic Arts",
    "price": 49,
    "genre": "Simulator",
    "platform": "PC",
    "avg_review": -1,
    "rating": "T",
    "release_date": "1994-08-31"
  }
]
 ```

SEARCH CATALOG

curl -X 'GET' \
  'https://redx-brri.onrender.com/catalog/search/?price=0&genre=Co-op&avg_review=0&sort_col=release_date&sort_order=desc' \
  -H 'accept: application/json'

   ```
[
  {
    "sku": "overcooked_0",
    "name": "OVERCOOKED",
    "publisher": "Ghost Town Games",
    "price": 22,
    "genre": "Co-op",
    "platform": "PlayStation",
    "avg_review": "NOT YET REVIEWED",
    "rating": "E",
    "release_date": "2024-05-10"
  },
  {
    "sku": "it_takes_two_0",
    "name": "IT TAKES TWO",
    "publisher": "Hazelight Studios",
    "price": 21,
    "genre": "Co-op",
    "platform": "PC",
    "avg_review": NOT YET REVIEWED,
    "rating": "E10",
    "release_date": "2021-03-26"
  }
]
```





CREATE CART

 curl -X 'POST' \
  'https://redx-brri.onrender.com/carts/' \
  -H 'accept: application/json' \
  -H 'access_token: redx' \
  -H 'Content-Type: application/json' \
  -d '{
  "account_id": 23
}'

```
{
    "account_id": 23
}

```

```
"cart_id 8"
```
CART VIEW 1
curl -X 'GET' \
  'https://redx-brri.onrender.com/carts/8' \
  -H 'accept: application/json' \
  -H 'access_token: redx'



```
  {
  "cart_id": 8,
  "customer_name": "Eugene Fitzherbert",
  "games_in_cart": [],
  "total_cost": 0,
  "checked_out": false
}
```


ADD TO CART

PART A

curl -X 'POST' \
  'https://redx-brri.onrender.com/carts/8/items/it_takes_two_0' \
  -H 'accept: application/json' \
  -H 'access_token: redx' \
  -d ''
  
RESPONSE

```
"OK"
```  
NOTE
cart items updates

ADD TO CART

PART B

curl -X 'POST' \
  'https://redx-brri.onrender.com/carts/8/items/animal_crossing_new_horizons_0' \
  -H 'accept: application/json' \
  -H 'access_token: redx' \
  -d ''

```
"OK"
```

NOTE
cart items updates


CART VIEW 2

curl -X 'GET' \
  'https://redx-brri.onrender.com/carts/8' \
  -H 'accept: application/json' \
  -H 'access_token: redx'

```
  {
  "cart_id": 8,
  "customer_name": "Eugene Fitzherbert",
  "games_in_cart": [
    "ANIMAL CROSSING: NEW HORIZONS",
    "IT TAKES TWO"
  ],
  "total_cost": 81,
  "checked_out": false
}
```


CHECKOUT

curl -X 'POST' \
  'https://redx-brri.onrender.com/carts/8/checkout' \
  -H 'accept: application/json' \
  -H 'access_token: redx' \
  -d ''

```
{
  "games_bought": 2,
  "total_price": 81
}
```

CART VIEW 3

curl -X 'GET' \
  'https://redx-brri.onrender.com/carts/8' \
  -H 'accept: application/json' \
  -H 'access_token: redx'
  
```
  {
  "cart_id": 8,
  "customer_name": "Eugene Fitzherbert",
  "games_in_cart": [
    "ANIMAL CROSSING: NEW HORIZONS",
    "IT TAKES TWO"
  ],
  "total_cost": 81,
  "checked_out": true
}
```


ADD REVIEW

curl -X 'POST' \
  'https://redx-brri.onrender.com/accounts/23/reviews/it_takes_two_0' \
  -H 'accept: application/json' \
  -H 'access_token: redx' \
  -H 'Content-Type: application/json' \
  -d '{
  "rating": 5
}'

```
{
  "rating": 5
}
```
```
RESPONSE

  "OK"


```

NOTE
response is okay
