import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
    TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/twitter_trends')