# database.py
import json
from motor.motor_asyncio import AsyncIOMotorClient
from utils.mongo import Document

# Load config files
with open("Configuration/config.json", "r") as f:
    GEN_CONFIG = json.load(f)

# Database Setup
db = AsyncIOMotorClient(GEN_CONFIG["MONGO_URL"])
tdb = db["TicketBot"]

ticket_db = Document(tdb, "tickets")
blacklisted_users = Document(tdb, "blacklisted_users")
