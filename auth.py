import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

import database.db_ops as dbs

# Load config from env
SECRET_KEY: Any = os.environ.get("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET not set")

ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "45"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode: Dict[str, Any] = {"sub": subject}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)    
        
    to_encode["exp"] = expire
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # jwt.encode may return bytes in some libs, ensure str
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify credentials against the DB.
    - Expects dbs.get_user(username) to return a user dict or None.
    - Stored password is expected to be a hashed password (bcrypt).
    """
    user = dbs.get_user(username)
    if not user:
        return None
    stored_pw = user["password"] # pyright: ignore[reportArgumentType]
    if stored_pw is None:
        return None
    # verify using passlib helper
    try:
        if verify_password(password, stored_pw):
            return user # type: ignore
    except Exception:
        # if verify fails, treat as non-authenticated
        return None
    return None


def _raise_unauthorized():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Dependency to get the current user from a bearer token.
    Decodes token, extracts 'sub' as username and fetches the user from DB.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        print("username", username)
        if not username:
            _raise_unauthorized()
    except Exception:
        _raise_unauthorized()

    user = dbs.get_user(username)  # pyright: ignore[reportPossiblyUnboundVariable]
    if user is None:
        _raise_unauthorized()
    return user # pyright: ignore[reportReturnType]
