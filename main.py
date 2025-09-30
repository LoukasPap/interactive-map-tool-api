from typing import Union, Annotated
import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from helpers import serialize_doc

from dotenv import load_dotenv
load_dotenv()

from database.db import get_db  # Import the singleton db accessor
db = get_db()

import database.db_ops as dbs
from models.TextSearchInput import TextSearchInput

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

 # Use the singleton db connection

@app.get("/")
def read_root():
    return {"MONGO_DB_NAME": MONGODB_NAME, "ORIGINS": ORIGINS}

 
@app.get("/search-text")
async def search_text(search_options: Annotated[TextSearchInput, Query()]):
    """Search the Points collection for documents matching the text query."""
    print(search_options.__repr__())
    try:
        results = await dbs.search_text(search_options.include_input, search_options.exclude_input, search_options.take_int_limit())
        print("Total documents", len(results))
        return {"features": results}
    
    except Exception as e:
        return {"error": f"Failed to search text. {e}"}


@app.get("/objects")
def get_objects():
    """Fetch all documents from the Points collection."""
    try:
        print("Fetching all data...")
        points = [serialize_doc(doc) for doc in db["Points"].find({})]
        print("Fetched all data!")
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