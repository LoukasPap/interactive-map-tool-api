from typing import Union
from dotenv import load_dotenv
import os

from pymongo import MongoClient # pyright: ignore[reportMissingImports]
from fastapi import FastAPI # pyright: ignore[reportMissingImports]

from pymongo.mongo_client import MongoClient # type: ignore
from pymongo.server_api import ServerApi # type: ignore

app = FastAPI()


load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")
ORIGINS = os.getenv("ORIGINS")


from fastapi.middleware.cors import CORSMiddleware # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGINS],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # allow all headers (Authorization, Content-Type, etc.)
)


client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
db = client[DB_NAME]


@app.get("/")
def read_root():
    return {"Hello": "World"}


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
    points = [serialize_doc(doc) for doc in db["Points"].find({"Type": "object"})]
    return {"features": points}

@app.get("/monuments")
def get_monuments():
    """Fetch all monuments from the Points collection."""
    points = [serialize_doc(doc) for doc in db["Points"].find({"Type": "monument"})]
    return {"features": points}