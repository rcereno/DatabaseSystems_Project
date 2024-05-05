import sqlalchemy
import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import auth
from enum import Enum

from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

# class search_sort_options(str, Enum):
#     customer_name = "customer_name"
#     item_sku = "item_sku"
#     line_item_total = "line_item_total"
#     timestamp = "timestamp"

# class search_sort_order(str, Enum):
#     asc = "asc"
#     desc = "desc"   

# @router.get("/search/", tags=["search"])
# def search_orders(
#     customer_name: str = "",
#     potion_sku: str = "",
#     search_page: str = "",
#     sort_col: search_sort_options = search_sort_options.timestamp,
#     sort_order: search_sort_order = search_sort_order.desc,
# ):
#     """
#     Search for cart line items by customer name and/or potion sku.

#     Customer name and potion sku filter to orders that contain the 
#     string (case insensitive). If the filters aren't provided, no
#     filtering occurs on the respective search term.

#     Search page is a cursor for pagination. The response to this
#     search endpoint will return previous or next if there is a
#     previous or next page of results available. The token passed
#     in that search response can be passed in the next search request
#     as search page to get that page of results.

#     Sort col is which column to sort by and sort order is the direction
#     of the search. They default to searching by timestamp of the order
#     in descending order.

#     The response itself contains a previous and next page token (if
#     such pages exist) and the results as an array of line items. Each
#     line item contains the line item id (must be unique), item sku, 
#     customer name, line item total (in gold), and timestamp of the order.
#     Your results must be paginated, the max results you can return at any
#     time is 5 total line items.
#     """

#     return {
#         "previous": "",
#         "next": "",
#         "results": [
#             {
#                 "line_item_id": 1,
#                 "item_sku": "1 oblivion potion",
#                 "customer_name": "Scaramouche",
#                 "line_item_total": 50,
#                 "timestamp": "2021-01-01T00:00:00Z",
#             }
#         ],
#     }


class Customer(BaseModel):
    customer_name: str
    customer_id: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    # notFirst = False

    # print(f"visit_id: {visit_id}")
    # print("[")
    # for customer in customers:
    #     if notFirst:
    #         print(f",\n\tLvl {customer.level} {customer.character_class}: {customer.customer_name}", end = '')
    #     else:
    #         print(f"\tLvl {customer.level} {customer.character_class}: {customer.customer_name}", end = '')
    #         notFirst = True
    
    # print("\n]")

        

    # print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """

    with db.engine.begin() as connection:

        cart_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO
                VALUES 
                """
            ),
            [{
                "customer_name": "dummy"
            }]
        ).scalar_one()

    return {"cart_id": cart_id}

@router.get("/{account_id}/{cart_id}")
def cart_view():

    return {
        "cart_id": 0, 
        "customer_name": "",
        "games_in_cart": [],  
        "total_cost": 0
    }


# class CartItem(BaseModel):
#     quantity: int

@router.post("/{cart_id}/items/{item_sku}")
# def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
def set_item_quantity(cart_id: int, item_sku: str):
    """ """

    # with db.engine.begin() as connection:       

        # gameId = connection.execute(
        #     sqlalchemy.text(
        #         "SELECT id FROM games WHERE sku = :item_sku"
        #     ),
        #     [{
        #         "item_sku": item_sku
        #     }]
        # ).scalar_one()

        # connection.execute(
        #     sqlalchemy.text(
        #         "INSERT INTO cart_items (cart_id, potion_id, quantity) VALUES (:cart_id, :potionId, :quantity)"
        #     ),
        #     [{
        #         "cart_id": cart_id,
        #         "potionId": potionId,
        #         "quantity": cart_item.quantity
        #     }]
        # )

    return "OK"


# class CartCheckout(BaseModel):
#     payment: str

@router.post("/{cart_id}/checkout")
# def checkout(cart_id: int, cart_checkout: CartCheckout):
def checkout(cart_id: int):
    """ """
    
    # with db.engine.begin() as connection:
    #     try:
    #         connection.execute(
    #             sqlalchemy.text(
    #                 "INSERT INTO processed (job_id, type) VALUES (:id, 'cart_checkout')"
    #             ),

    #             [{
    #                 "id": cart_id
    #             }]
    #         )
    #         # LEDGERIZING
    #         transaction_id = connection.execute(
    #             sqlalchemy.text(
    #                     "INSERT INTO transactions (type, description) VALUES ('cart checkout', 'did not set description yet') RETURNING id"
    #                 )
    #         ).scalar_one()
    #     except IntegrityError as e:
    #         print("OMG THE CART CHECKOUT DIDN'T GO THROUGH")
    #         return {"total_potions_bought": 0, "total_gold_paid": 0}


        # for cart_items in results:



        # LEDGERIZING



    return {"games_bought": 0, "total_price": 0}
