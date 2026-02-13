import os
from dotenv import load_dotenv

# .env file se passwords load karo
load_dotenv()

# Settings
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-please-change")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60