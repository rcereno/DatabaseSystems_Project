# API Specification for REDX

## 1. Customer Purchasing

The API's:

1. `Get Catalog`
2. `New Cart`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`
5. `Search Orders`
6. `catalog search`
7. `Account view`
8. `Add to wish list`
9. `Review game`

### 1. Get Catalog - `/catalog/` (GET)

Retrieves the catalog of items. Each unique item combination should have only a single price.

**Response**:

```json
[
  {
    "sku": "string" /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */,
    "name": "string",
    "publisher": "string",
    "price": "integer" /* Between 1 and 500 */,
    "genre": "string",
    "platform": "string",
    "mode_review": "integer" /*between 1-5 for 1-5 stars*/,
    "rating": "string" /*Rating for the game*/
  }
]
```

### 2. New Cart - `/carts/` (POST)

Creates a new cart for a specific customer.

**Request**:

```json
{
  "account_id": "integer"
}
```

**Response**:

```json
{
  "cart_id": "string" /* This id will be used for future calls to add items and checkout */
}
```

### 3. Add Item to Cart - `/carts/{cart_id}/{item_sku}` (PUT)

Updates a specific game in a cart. Will update their cart in the cart_items table with the game they've added.

**Request**:

**Response**:

```json
{
  "success": "boolean"
}
```

### 4. Checkout Cart - `/carts/{cart_id}/checkout` (POST)

Handles the checkout process for a specific cart.

**Request**:

```json
{
  "payment": "string"
}
```

**Response**:

```json
{
  "games_bought": "integer",
  "total_price": "integer"
}
```

### 5. View Cart - `/carts/{account_id}/{cart_id}` (POST)

View current cart of the customer

**Response**:

```json
{
  "cart_id": "integer",
  "customer_name": "string",
  "games_in_cart": "integer",
  "total_cost": "integer"
}
```

### 6. Search Games in Catalog - `/catalog/search/` (GET)

Searches for games based on specified query parameters.

**Query Parameters**:

- `game_sku` (optional): The SKU of the game.
- `search_page` (optional): The page number of the search results.
- `sort_col` (optional): The column to sort the results by. Possible values: `game_name`, `price`, `publisher`, `platform`, `mode_review`, `genre`, `release_date`. Default: `release_date`.
- `sort_games` (optional): The sort order of the results. Possible values: `asc` (ascending), `desc` (descending). Default: `desc`.

**Response**:

The API returns a JSON object with the following structure:

- `previous`: A string that represents the link to the previous page of results. If there is no previous page, this value is an empty string.
- `next`: A string that represents the link to the next page of results. If there is no next page, this value is an empty string.
- `results`: An array of objects, each representing a line item. Each line item object has the following properties:
  - `game_sku`: A string that represents the SKU of the game.
  - `price`: An integer representing the price of the game
  - `publisher`: A string that represents the publisher of the game
  - `platform`: A string that represents the platform the game is available on.
  - `mode_review`: A number representing the most frequently given star review.
  - `genre`: A string representing the genre of the game.
  - `family_rating `: A string representing the rating of the game.
  - `release_date`: A string that represents the date and time when the game was released. This is in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).

### 7. Account Management

### 7.1 Account Registration - `/register/{account_id}` (POST)

A call customers can make to register their account.

**Request**:

```json
{
  "customer_name": "string",
  "email": "string"
}
```

**Response**

```json
{
  "success": "boolean",
  "msg": "string"
}
```

### 7.2 Account View- `/{account_id}/view` (GET)

**Reponse**

```json
{
  "customer_name": "string",
  "games_owned": ["string"], /*an array of strings representing the names of games that the customer owns*/,
  "wishlist": ["string"], /*an array of strings representing the names of games that the customer wants*/,
  "current_cart": "Games in cart: {games_in_cart}, Cost: {cost}" /*string showing current cart contents*/
}
```

### 8. Add to wishlist- `/{account_id}/wishlist/{game_sku}` (PUT)

An API call that allows a customer to add a specific game to their account wishlist.

**Reponse**

```json
{
  "success": "boolean",
  "msg": "string"
}
```

### 9. Review game- `/{account_id}/reviews/{game_sku}` (PUT)

An API call that allows a customer to review a game.

**Reponse**

```json
{
  "success": "boolean",
  "msg": "string"
}
```

### 4. Admin Functions

### 4.1. Reset Shop - `/admin/reset` (POST)

A call to reset shop will delete all inventory and in-flight carts and reset gold back to 100. The
shop should take this as an opportunity to remove all of their inventory and set their gold back to
100 as well.

### 9. Review game - '/games/{game_id}/reviews' (PUT)

Add review of up to five stars into a game's review data.

**Request:**

```json
{
  "game_id": "integer",
  "account_id": "integer",
  "review": "integer" /*1-5 for 5 stars*/
}
```

**Response:**

```json
{
  "success": "boolean"
}
```
