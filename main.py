from fastapi import FastAPI, status, APIRouter, HTTPException, Query, Path, Depends

from typing import Annotated
import os

from fastapi.middleware.cors import CORSMiddleware

from helpers import serialize_doc

from dotenv import load_dotenv
load_dotenv()

from database.db import get_db  # Import the singleton db accessor
db = get_db()

import database.db_ops as dbs
from models.TextSearchInput import TextSearchInput
from models.UserModels import *
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import auth as auth_module
from datetime import datetime

app = FastAPI()
auth_router = APIRouter(prefix="/auth")
collection_router = APIRouter(prefix="/collections")

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


@app.get("/")
def read_root():
    return {"Hello": "World!"}


# Findings Routes

@app.get("/search-text", tags=["findings"])
async def search_text(search_options: Annotated[TextSearchInput, Query()]):
    """Search the Points collection for documents matching the text query."""
    print(search_options.__repr__())
    try:
        results = await dbs.search_text(search_options.include_input, search_options.exclude_input, search_options.take_int_limit())
        print("Total documents", len(results))
        return {"features": results}
    except Exception as e:
        return {"error": f"Failed to search text. {e}"}


projection: dict[str, int] = {"_id": 0, "Name": 1, "Title": 1, "Type": 1, "geometry": 1, "Era": 1, 
                                "InventoryNumberLetter": 1, "MaterialCategory": 1, "CleanCondition": 1, 
                                "SectionNumber": 1, "SectionNumberLetter": 1, "SectionNumberNumber": 1, "Images": 1}

@app.get("/findings", tags=["findings"])
async def get_findings_ids():
    res = db["Points"].find({}, projection).to_list()
    return { "features": res }


@app.get("/findings/{Name}", tags=["findings"])
def get_finding_by_name(Name: str):
    res = db["Points"].find_one({"Name": Name})
    if res:
        serialized_doc = serialize_doc(res)
        return {"point": serialized_doc}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding with Name {Name} not found"
        )




# Authorization Routes

@auth_router.post("/register", tags=["authorization"])
async def register_user(body: UserRegister):
    """Register new user in the database"""
    
    print("Begin Register:", body)
    if dbs.user_exists(body.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"username": "Username already exists"}
        )
    
    # hash the password before saving using auth module helper
    user_data = body.model_dump()
    user_data["password"] = auth_module.get_password_hash(user_data["password"])
    await dbs.register_user(user_data)
    
    print("Finish Registering:")
    
    return JSONResponse(status_code=200, content={"message": "User created"})


@auth_router.post("/login", tags=["authorization"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint that returns a JWT access token.
    """
    # OAuth2PasswordRequestForm provides .username and .password
    username = form_data.username
    password = form_data.password

    user = auth_module.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_module.create_access_token(subject=user.get("username") or username)
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/verify", tags=["authorization"])
async def verify_token(current_user: dict = Depends(auth_module.get_current_user)):
    """
    Verify the provided bearer token. Returns minimal user info if valid.
    """
    return {"valid": True, "user": {"username": current_user.get("username")}}



# Collections Routes
@collection_router.post("", tags=["collections"])
async def create_collection(collection: CollectionCreate):
    print("Creating collection:", collection)
    db["Collections"].insert_one(collection.model_dump())
    return {"message": f"Collection created {collection}"}


@collection_router.put("/{id}", tags=["collections"])
async def update_collection(updatedCollection: Collection, id: Annotated[str, Path(title="The id of the collection to update")]):
    print("Inside", id, "----", updatedCollection)
    db["Collections"].find_one_and_update(
        {"id": id},
        {"$set": updatedCollection.model_dump()}
    )
    
    return {"message": f"Collection with id {id} updated"}


@collection_router.delete("/{id}", tags=["collections"])
async def delete_collection(id: Annotated[str, Path(title="The id of the collection to delete")]):
    res = db["Collections"].find_one_and_delete({"id": id})
    if res:
        return {"message": f"Collection with {id} deleted"}
    
    return {"message": f"Collection with {id} not found"}


@collection_router.get("/{owner}", tags=["collections"])
async def get_collections(owner: Annotated[str, Path(title="The username of the user")]):
    res = db["Collections"].find({"owner": owner})
    if res is not None:
        docs = [serialize_doc(doc) for doc in res]
        return {"data": docs}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No collections found for owner {owner}"
        )
        


app.include_router(auth_router)
app.include_router(collection_router)
