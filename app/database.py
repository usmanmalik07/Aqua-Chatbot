from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection string from environment variable
MONGODB_URL = os.getenv("MONGODB_URL")

# Initialize MongoDB client
client = MongoClient(MONGODB_URL)

def connect_to_mongo():
    return client

def get_database():
    db_name = "your_database_name"  # replace with your actual database name
    return client[db_name]
