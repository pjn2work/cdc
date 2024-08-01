import hashlib
import os
from datetime import timedelta, datetime
from typing import List

from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app import logit
from app.utils import read_json_file, b64decode_str

cred = read_json_file("../../data/credentials.json", same_as=__file__)

SALT = cred.get("salt", "")
APP_CLIENTS = cred["app_clients"]
SECRET_KEY = cred["app_secret_key"] or os.getenv("CECC_SECRET_KEY", "not_secured")
ALGORITHM = "HS256"
MAX_ACCESS_TOKEN_EXPIRE = 24


router = APIRouter()

pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth/token")


class Client(BaseModel):
    client_name: str | None = None
    client_secret: str | None = None
    scopes: List[str] = []
    expire_after: float = 1.0


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    client_id: str | None = None
    scopes: List[str] = []


def hash_password(plain_password: str) -> str:
    plain_password += SALT
    password_bytes = plain_password.encode('utf-8')

    hash_object = hashlib.sha256()
    hash_object.update(password_bytes)

    hashed_password = hash_object.hexdigest()
    return hashed_password


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


def _get_client_by_id(client_id: str) -> Client | None:
    client = APP_CLIENTS.get(client_id)
    if client is None:
        return None
    return Client(**client)


def _verify_client(client_id: str, client_secret: str) -> Client | None:
    client = _get_client_by_id(client_id)
    if client and _verify_password(client_secret, client.client_secret):
        return client
    return None


def _create_access_token(data: dict, expire_hours: float) -> str:
    expire = datetime.utcnow() + timedelta(hours=min(expire_hours, MAX_ACCESS_TOKEN_EXPIRE))
    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_access_token(client_id: str, client_secret: str) -> dict:
    client: Client = _verify_client(client_id, client_secret)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect client_id or client_secret",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = _create_access_token(
        data={
            "sub": client_id,
            "scopes": client.scopes
        },
        expire_hours=client.expire_after
    )
    logit(f"Client Successful login: {client.client_name} - expire after {client.expire_after}h")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/hash", response_model=Client)
def make_hash_password(plain_password: str=""):
    return Client(client_secret=hash_password(plain_password))


@router.post("/token", response_model=Token)
async def login_for_access_token(
        request: Request = None,
        cc: str = ""):
    if cc:
        # for m2m use (in the future)
        client_id, client_secret = b64decode_str(cc).split(":")
    else:
        # OIDC (for swagger)
        data = await request.form()
        client_id = data.get("client_id") or data.get("username")
        client_secret = data.get("client_secret") or data.get("password")

    return get_access_token(client_id, client_secret)


def _get_current_client(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id: str = payload.get("sub")
        scopes: List[str] = payload.get("scopes", [])

        client = _get_client_by_id(client_id)
        if client_id is None or client is None:
            raise credentials_exception

        token_data = TokenData(client_id=client_id, scopes=client.scopes)
    except JWTError:
        raise credentials_exception

    return token_data


async def get_current_api_client(token: str = Depends(oauth2_scheme)) -> TokenData:
    return _get_current_client(token)


async def get_current_web_client(request: Request) -> TokenData:
    token = request.cookies.get("access_token")
    return _get_current_client(token)


def are_valid_scopes(necessary_scopes: List[str], current_client: TokenData) -> str:
    for scope in necessary_scopes:
        if scope in current_client.scopes:
            return scope
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
