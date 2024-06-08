import os
import dotenv
import sqlalchemy
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)
metadata_obj = sqlalchemy.MetaData()
carts = sqlalchemy.Table("carts", metadata_obj, autoload_with=engine)
accounts = sqlalchemy.Table("accounts", metadata_obj, autoload_with=engine)
cart_items = sqlalchemy.Table("cart_items", metadata_obj, autoload_with=engine)
wishlisted = sqlalchemy.Table("wishlisted", metadata_obj, autoload_with=engine)
purchased = sqlalchemy.Table("purchases", metadata_obj, autoload_with=engine)
games = sqlalchemy.Table("games", metadata_obj, autoload_with=engine)

metadata_obj.reflect(bind=engine, views=True)
game_catalog = sqlalchemy.Table("game_catalog", metadata_obj, autoload_with=engine)
