from pymongo import MongoClient
from info import MONGO_URI_MAIN

client = MongoClient(MONGO_URI_MAIN)
db = client["vjbot"]

settings = db["settings"]
users = db["users"]
channels_col = db["channels"]

def get_verify_link():
    cfg = settings.find_one({"_id": "links"})
    if cfg and "verify_link" in cfg:
        return cfg["verify_link"]
    return "https://yourdomain.com/direct_video.mp4"

def get_tutorial_link():
    cfg = settings.find_one({"_id": "links"})
    if cfg and "tutorial_link" in cfg:
        return cfg["tutorial_link"]
    return "https://t.me/your_tutorial"

def update_links(verify_link=None, tutorial_link=None):
    data = {}
    if verify_link:
        data["verify_link"] = verify_link
    if tutorial_link:
        data["tutorial_link"] = tutorial_link
    if data:
        settings.update_one({"_id": "links"}, {"$set": data}, upsert=True)

def save_user_data(user_id, data):
    users.update_one({"user_id": user_id}, {"$set": data}, upsert=True)

def log_to_channel(bot, message_text):
    from info import LOG_CHANNEL
    if LOG_CHANNEL:
        try:
            bot.send_message(LOG_CHANNEL, message_text)
        except:
            pass
