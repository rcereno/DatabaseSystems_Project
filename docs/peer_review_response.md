## Code peer suggestions

1. Add docstrings to endpoint functions where they don't exist: added docstrings to every endpoint for clarity
2. Add more commenting: added more guiding comments throughout code to explain what it does more clearly
3. Refactor catalog search, remove if/elif statements: changed to mapping our sort columns to the correct database column, just requires one get instead
4. Search catalog parameters could be moved to a class to make the function’s argos easier to read/edit: The search sort col/sort order parameters are in a class already and we think the arguments are understandable/easily alterable as is.
5. Remove commented out code: removed unneccessary commented out code
6. Remove inventory/audit: We do not want to remove this as we want en endpoint that retrieves the shop's total games owned, sold and money made.
7. Cart view: Combine the two queries into one with joins
8. Make sure cart view is consistent with API spec
9. More try/except statements
10. Set_item_quantity: combine separate select and insert sql queries into one sql query that inserts based on the select
11. Cart checkout: combine select and insert statement for games_bought and purchased into one
12. In cart_checkout, no need for order_by when getting account_id since cart_id is unique already. (originally had this bc a single account may have multiple carts and wanted the most recent one, but doesn’t matter in this case)
13. Getting the games_in_cart and total_cost from the cart row of Carts is not storing the data in Carts.
14. Move sql metadata to database.py file and then import the metadata into each individual api file: Completed as suggested
15. Reassess the necessity of the UPDATE query for maintaining data integrity
16. Eliminate the redundant storage of these values in the carts table: the games_bought and total_cost are not redundant as a cart may have multiple cart_items rows referring to it. (ex: when someone has more than 1 game in their cart). We store it so that we don’t have to sum it up every time if we want to get the amount for a specific cart.

## API/Schema peer suggestions

1. Get catalog: change the max character length (20 is too short): Changed it to 50
2. Add item to cart: There is no request body for this API, you just use parameters like in potion shop.
3. Account registration: return account id: Now registration returns account_id to user
4. cart_view API inconsistent w/ implementation (cart view now)
5. Add to wishlist: inconsistent w/ implementation
6. Remove current time
7. Review game: implementation and spec inconsistent
8. Not storing total_games and total_cost for each cart, instead do a cart view that has the information for each cart
9. Remove comments
10. Price to dollars instead of cents
11. Make columns like sku, name, and price in the games table not nullable
12. Authentication endpt to prevent customers from taking data from another customer’s cart
13. Remove from wishlist endpt
14. Add the body to the post request on reset shop. Needs the customer ID and cart to reset. Also should update the description since it seems to still be describing the potion shop.
15. Fix formatting in audit fcn spec “number_of_games” is missing a quotation mark
16. API 8 (Add to Wishlist): Modify the request payload to include the item SKU instead of the customer name for clarity: There is no request body since all the information needed is in the endpoint url w/ account_id and game_sku
17. SQL Schema (carts table): Calculate total games and total cost from cart items to minimize data redundancy and update overhead: We are already doing this?. Consider implementing ledgers to keep these values updated.
18. Remove commented out code segments
19. SQL Schema (carts for accounts): Incorporate a "current cart" column in the accounts table to link to the current open cart, reducing redundancy and boosting efficiency.

## Testing results

## Product Suggestions Peer Response

Game testing

- We did not feel this was complex enough and we already had an idea to do game recommendations.

Game trade in or game trading between accounts

- We did not implement this since our service does not track credits as of right now. Trading games between accounts would not be complex enough since it’s just updating rows in our purchases
  table to change the account_id associated with a game.

Game progression tracker / dynamic in game events

- Our service is more so to sell games but not a game itself that does events such as these. It would also be difficult to do since you cannot “play” games using our endpoints.

Favoriting system

- We already have a system like this, wishlisting is essentially favoriting a game without buying it.

Request for a game?

- Due to the lack of detail given, we were unsure what exactly this suggestion meant.
