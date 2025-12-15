from dotenv import load_dotenv
from sqlalchemy import URL
import os

load_dotenv()

# url_object = URL.create(
#     drivername = os.getenv("db_drivername"),
#     username = os.getenv("db_username"),
#     password = os.getenv("db_password"),
#     host = os.getenv("db_host"),
#     port = os.getenv("db_port"),
#     database = os.getenv("db")
# )

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")