from pymongo import MongoClient

db = None

def init_db(app):
    global db
    client = MongoClient(app.config['MONGODB_URI'])
    db = client.get_default_database()
    return db

def get_db():
    return db