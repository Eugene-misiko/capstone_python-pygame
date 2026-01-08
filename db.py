import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env")

client = MongoClient(MONGO_URI)
db = client["pygame_game"]
players = db["players"]

def create_player(username):
    if not players.find_one({"username": username}):
        players.insert_one({
            "username": username,
            "level": 1,
            "wins": 0,
            "losses": 0,
            "recovery": False
        })

def get_player(username):
    return players.find_one({"username": username})

def update_stats(username, win=False):
    if win:
        players.update_one(
            {"username": username},
            {"$inc": {"wins": 1}, "$set": {"recovery": False}}
        )
    else:
        players.update_one(
            {"username": username},
            {"$inc": {"losses": 1}, "$set": {"recovery": True}}
        )

def set_level(username, level):
    players.update_one({"username": username}, {"$set": {"level": level}})

def level_up_player(username):
    players.update_one({"username": username}, {"$inc": {"level": 1}})

def consume_recovery(username):
    players.update_one({"username": username}, {"$set": {"recovery": False}})

def get_leaderboard(limit=5):
    return list(players.find().sort("wins", -1).limit(limit))




    



