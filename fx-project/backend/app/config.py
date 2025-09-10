from dotenv import load_dotenv
import os
load_dotenv()

MOCK = os.getenv("MOCK", "1") == "1"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "fx")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
