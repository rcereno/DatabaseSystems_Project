- Exception: Credit card gets declined
  - If a user's credit card gets declined when checking out of their cart, the cart will give back an error to the user and ask them to try a different credit card instead.

- Exception: User provides an invalid category or platform when browsing 
  - If a user provides the name of a category or platform that does not exist within the database, an error will be given back and gives the selection of categories or platforms (respectively)

- Exception: User leaves a review that goes over the character limit
  - If a user writes too long of a message as a review, an error will notify them of the accepted character length

- Exception: User leaves a review that violates our guidelines
  - If a user leaves a review of vulgar/offensive content, and error will notify the user that such language will not be tolerated, giving the user a warning or a temporary ban for multiple offenses.
 
- Exception: Inventory Availability
  - If a user tries to purchase a game that is out of stock or no longer available, the system will notify the user immediately, remove the item from the cart, and may suggest similar alternatives.

- Exception: Payment Processing Timeout
  - If the payment process times out due to network or server issues, the system will inform the user of the timeout and offer options to retry the payment or select an alternative payment method.

- Exception: Data Modification Error
  - If an admin encounters an error while trying to modify critical data (like user information or inventory updates), the system will notify the admin of the error and may suggest retrying the operation.

- Exception: Account Login Failure
  - If a user fails to log in due to incorrect credentials or a suspended account, the system will alert the user, offer the option to reset the password, and provide guidance on unlocking the account.

- Exception: Promotional Code Error
  - If a user enters an expired or invalid promotional code, the system will display a message indicating that the code is invalid or expired and prompt the user to try a different code.

- Exception: Shipping Restrictions
  - If a user selects a shipping address where certain items can't be shipped due to legal restrictions or shipping limitations, the system will notify the user and request an alternative shipping address or remove the restricted items from the cart.

- Exception: User attempts to buy a game that used to be on sale, but no longer is on sale
  - If a game that was previously on sale is in a user's cart, but the sale period has finished, the user will be notified and ask whether they still wish to purchase the game
 
- Exception: User has insufficient credits to purchase a game
  - If a user tries to buy a game with insufficient credits (from a gift card), an error message will occur and request to also put credit card information to cover the rest of the cost

