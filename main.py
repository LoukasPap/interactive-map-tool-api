from typing import Union
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from db import get_db  # Import the singleton db accessor

app = FastAPI()

MONGODB_NAME = os.environ.get("MONGODB_DB")
ORIGINS: str = str(os.environ.get("ORIGINS"))

if not os.environ.get("MONGODB_URI"):
    raise RuntimeError("MONGODB_URI not set")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGINS],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # allow all headers (Authorization, Content-Type, etc.)
)

db = get_db()  # Use the singleton db connection

@app.get("/")
def read_root():
    return {"MONGO_DB_NAME": MONGODB_NAME, "ORIGINS": ORIGINS}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Helper to convert ObjectId to string for JSON
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@app.get("/objects")
def get_objects():
    """Fetch all documents from the Points collection."""
    try:
        points = [serialize_doc(doc) for doc in db["Points"].find({"Type": "object"})]
        return {"features": points}
    except Exception as e:
        return {"error": f"Failed to fetch objects. {e}"}

@app.get("/monuments")
def get_monuments():
    """Fetch all monuments from the Points collection."""
    try:
        print("Fetching...")
        points = [serialize_doc(doc) for doc in db["Points"].find({"Type": "monument"})]
        print("Fetched!")
        return {"features": points}
    except Exception as e:
        return {"error": f"Failed to fetch monuments. {e}"}