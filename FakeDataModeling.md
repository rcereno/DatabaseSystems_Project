# Fake Data Modeling
## Data Distribution
To make a dataset with around one million rows, the data was spread out like this:

- Games: 5,000 records
- Accounts: 200,000 records
- Carts: 200,000 records
- Cart Items: 100,000 records
- Purchases: 200,000 records
- Reviews: 95,000 records
- Wishlists: 200,000 records

The total number of rows across all tables is 1,000,000.

## Justification
The data was spread out this way based on these thoughts:

1. **Games**: Having 5,000 different games gives a good selection for a gaming platform.

2. **Accounts**: With 200,000 user accounts, it looks like a big user base. This lets us test user sign-in, profiles, and personal features.

3. **Carts**: Having 200,000 carts (same as accounts) means each user may have an active cart. This lets us test how carts work.

4. **Cart Items**: With 100,000 cart items (less than carts), it means not all carts have items. This tests how cart items work with carts.

5. **Purchases**: Having 200,000 purchases (same as accounts) means many users made at least one purchase. This lets us test purchase history, orders, and money made.

6. **Reviews**: With 95,000 reviews, it looks like users give a lot of feedback on games. This lets us test how reviews are made, collected, and shown.

7. **Wishlists**: Having 200,000 wishlisted items (same as accounts) means users have multiple games on their wishlists. This lets us test how wishlists work, recommendations, and user involvement.

The way the data is spread out tries to look realistic while having enough data for testing. It thinks about how different data connects and how users might behave. But real systems may be different based on how many users join, stay, and get involved. This spread of data is a good start for testing and can be changed as needed.
