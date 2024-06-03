## Code peer suggestions

1. Add docstrings to endpoint functions where they don't exist: completed
2. Add more commenting
3. Refactor catalog search, remove if/elif statements
4. Search catalog parameters could be moved to a class to make the function’s argos easier to read/edit
5. Remove commented out code
6. Remove inventory/audit: We do not want to remove this as we want en endpoint that retrieves the shop's total games owned, sold and money made.
7. Cart view: Combine the two queries into one with joins
8. Make sure cart view is consistent with API spec
9. More try/except statements
10. Set_item_quantity: combine separate select and insert sql queries into one sql query that inserts based on the select
11. Cart checkout: combine select and insert statement for games_bought and purchased into one
12. In cart_checkout, no need for order_by when getting account_id since cart_id is unique already. (originally had this bc a single account may have multiple carts and wanted the most recent one, but doesn’t matter in this case)
13. Getting the games_in_cart and total_cost from the cart row of Carts is not storing the data in Carts.
14. Move sql metadata to database.py file and then import the metadata into each individual api file
15. Reassess the necessity of the UPDATE query for maintaining data integrity
16. Eliminate the redundant storage of these values in the carts table: the games_bought and total_cost are not redundant as a cart may have multiple cart_items rows referring to it. (ex: when someone has more than 1 game in their cart). We store it so that we don’t have to sum it up every time if we want to get the amount for a specific cart.

## API/Schema peer suggestions

## Testing results

## Product Suggestions Peer Response
