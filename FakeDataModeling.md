# Fake Data Modeling

## Python Script
The script that makes the fake data is:

import sqlalchemy
import os
import dotenv
from faker import Faker
from datetime import datetime, timedelta
import time
import random

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = "postgres.noxklrtxzeynqmzwchut"
    DB_PASSWD = "zoW07qlywm9zA87g"
    DB_SERVER: str = "aws-0-us-west-1.pooler.supabase.com"
    DB_PORT: str = "6543"
    DB_NAME: str = "postgres"
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}?connect_timeout=300"

engine = sqlalchemy.create_engine(database_connection_url(), pool_size=20, max_overflow=0)
fake = Faker()

num_accounts = 200000
num_carts = 200000
num_cart_items = 100000
num_purchases = 200000
num_reviews = 95000
num_wishlisted = 200000
num_games = 5000

batch_size = 10000
max_retries = 3
retry_delay = 1  # seconds

with engine.begin() as conn:
    # Set the statement timeout
    conn.execute(sqlalchemy.text("SET statement_timeout = 600000"))

    # Generate games
    print("Generating games...")
    games = []
    for _ in range(num_games):
        games.append({
            'item_sku': fake.unique.bothify(text='????-########'),
            'name': fake.catch_phrase(),
            'publisher': fake.company(),
            'price_in_dollars': fake.random_int(min=10, max=100),
            'platform': fake.random_element(elements=['PC', 'Xbox', 'PlayStation', 'Nintendo']),
            'genre': fake.word(),
            'family_rating': fake.random_element(elements=['E', 'E10+', 'T', 'M']),
            'release_date': fake.date_between(start_date='-10y', end_date='today')
        })

    conn.execute(sqlalchemy.text("INSERT INTO games (item_sku, name, publisher, price_in_dollars, platform, genre, family_rating, release_date) VALUES (:item_sku, :name, :publisher, :price_in_dollars, :platform, :genre, :family_rating, :release_date) ON CONFLICT DO NOTHING"), games)
    print("Games generated.")

    existing_game_ids = conn.execute(sqlalchemy.text("SELECT id FROM games")).scalars().all()

    # Generate accounts
    print("Generating accounts...")
    accounts = []
    while len(accounts) < num_accounts:
        email = fake.unique.email()
        accounts.append({
            'email': email,
            'name': fake.name(),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        })

    for i in range(0, num_accounts, batch_size):
        batch_accounts = accounts[i:i+batch_size]
        try:
            conn.execute(sqlalchemy.text("INSERT INTO accounts (email, name, created_at) VALUES (:email, :name, :created_at) ON CONFLICT DO NOTHING"), batch_accounts)
        except sqlalchemy.exc.IntegrityError:
            pass

    print("Accounts generated.")

    existing_account_ids = conn.execute(sqlalchemy.text("SELECT id FROM accounts")).scalars().all()

    # Generate carts
    print("Generating carts...")
    carts = []
    for _ in range(num_carts):
        carts.append({
            'account_id': random.choice(existing_account_ids),
            'created_at': fake.date_time_between(start_date='-1y', end_date='now'),
            'checked_out': fake.boolean(chance_of_getting_true=25)
        })
    conn.execute(sqlalchemy.text("INSERT INTO carts (account_id, created_at, checked_out) VALUES (:account_id, :created_at, :checked_out)"), carts)
    print("Carts generated.")

    existing_cart_ids = conn.execute(sqlalchemy.text("SELECT id FROM carts")).scalars().all()

    # Generate cart items
    print("Generating cart items...")
    cart_items = []
    for _ in range(num_cart_items):
        cart_id = random.choice(existing_cart_ids)
        game_id = random.choice(existing_game_ids)
        cost = conn.execute(sqlalchemy.text("SELECT price_in_dollars FROM games WHERE id = :game_id"), {'game_id': game_id}).scalar()
        cart_items.append({
            'cart_id': cart_id,
            'game_id': game_id,
            'cost': cost,
            'created_at': fake.date_time_between(start_date='-1y', end_date='now')
        })

    for i in range(0, num_cart_items, batch_size):
        batch_cart_items = cart_items[i:i+batch_size]
        retries = 0
        while retries < max_retries:
            try:
                conn.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, game_id, cost, created_at) VALUES (:cart_id, :game_id, :cost, :created_at)"), batch_cart_items)
                print(f"Inserted {i+len(batch_cart_items)} cart items")
                break
            except sqlalchemy.exc.IntegrityError as e:
                retries += 1
                print(f"Retry {retries}/{max_retries} - Error: {str(e)}")
                time.sleep(retry_delay)

    print("Cart items generated.")

    # Generate purchases
    print("Generating purchases...")
    purchases = []
    for _ in range(num_purchases):
        account_id = random.choice(existing_account_ids)
        game_id = random.choice(existing_game_ids)
        purchases.append({
            'account_id': account_id,
            'game_id': game_id,
            'money_given': conn.execute(sqlalchemy.text("SELECT price_in_dollars FROM games WHERE id = :game_id"), {'game_id': game_id}).scalar(),
            'created_at': fake.date_time_between(start_date='-1y', end_date='now')
        })
    conn.execute(sqlalchemy.text("INSERT INTO purchases (account_id, game_id, money_given, created_at) VALUES (:account_id, :game_id, :money_given, :created_at) ON CONFLICT DO NOTHING"), purchases)
    print("Purchases generated.")

    # Generate reviews
    print("Generating reviews...")
    reviews = []
    for _ in range(num_reviews):
        account_id = random.choice(existing_account_ids)
        game_id = random.choice(existing_game_ids)
        reviews.append({
            'account_id': account_id,
            'game_id': game_id,
            'review': random.randint(1, 5),
            'created_at': fake.date_time_between(start_date='-1y', end_date='now')
        })
    conn.execute(sqlalchemy.text("INSERT INTO reviews (account_id, game_id, review, created_at) VALUES (:account_id, :game_id, :review, :created_at) ON CONFLICT DO NOTHING"), reviews)
    print("Reviews generated.")

    # Generate wishlists
    print("Generating wishlists...")
    wishlists = []
    for _ in range(num_wishlisted):
        account_id = random.choice(existing_account_ids)
        game_id = random.choice(existing_game_ids)
        wishlists.append({
            'account_id': account_id,
            'game_id': game_id,
            'created_at': fake.date_time_between(start_date='-1y', end_date='now')
        })
    conn.execute(sqlalchemy.text("INSERT INTO wishlisted (account_id, game_id, created_at) VALUES (:account_id, :game_id, :created_at) ON CONFLICT DO NOTHING"), wishlists)
    print("Wishlists generated.")

print("Data generation completed.")

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
