
# Fake Data Modeling
Should contain a link to the python file you used to construct the million rows of data for your service. Should also contain a writeup explaining how many final rows of data you have in each of your table to get to a million rows AND a justification for why you think your service would scale in that way. There is no single right answer to this, but your reasoning must be justifiable.

#### Link to python file: (insert here)

#### Write-up:
To get to a million rows of data, the amount of final rows of data that we needed to each to get to a million rows was adding a million rows to our games catalog and our reviews database (note to team: feel free to adjust based on type of data we populated/constructed). [explain what script does here]. To justify why we think our service would scale in this way is due to the way we set up our shop as an e-commerce game store for gamers  and assuming that our intended audience of gamers would wishlist, buy, or place the games in their carts based off of the reviews or recommendations, in terms of how recommendations are created from owned games and reviews, given to them. 

# Performance Results of Hitting Points
For each endpoint, list how many ms it took to execute. State which three endpoints were the slowest.

### Amount of ms it took to execute each endpoint: 

### Cart

#### /carts/

#### /carts/{cart_id}

#### /carts/{cart_id}/items/{items_sku}

#### /carts/{cart_id}/checkout

### Catalog

#### /catalog

#### /catalog/trending/

### Search

#### /catalog/search/

### Accounts

#### /accounts/register

#### /accounts/{account_id}/view

#### /accounts/{account_id}/reviews/{game_sku}

#### /accounts/{account_id}/wishlist/{game_sku}

#### /accounts/{account_id}/recommend

### Admin

#### /admin/reset

### Games

#### /games/add

### The Three Slowest Endpoints:

1. 
2. 
3. 

# Performance Tuning
For each of the three slowest endpoints, run explain on the queries and copy the results of running explain into the markdown file. Then describe what the explain means to you and what index you will add to speed up the query. Then copy the command for adding that index into the markdown and rerun explain. Then copy the results of that explain into the markdown and say if it had the performance improvement you expected. Continue this process until the three slowest endpoints are now acceptably fast (think about what this means for your service).

1. 

2. 

3. 