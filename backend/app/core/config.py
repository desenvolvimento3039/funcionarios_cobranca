import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "10.22.14.5")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "@sicoob1010")
DB_NAME = os.getenv("DB_NAME", "LeCom")
PORT = int(os.getenv("PORT", "8586"))
