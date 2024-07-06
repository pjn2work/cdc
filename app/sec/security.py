from datetime import timedelta, datetime
from typing import List

from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..utils import read_json_file

cred = read_json_file("../../credentials.json", same_as=__file__)

# default_cecc_password
APP_CLIENTS = cred["app_clients"]
SECRET_KEY = cred["cecc_secret_key"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(seconds=10)


router = APIRouter()

pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sec/token")


class Client(BaseModel):
    client_name: str | None = None
    client_secret: str | None = None
    scopes: List[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    client_id: str | None = None
    scopes: List[str] = []


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        return False


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


def _create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE
    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_access_token(client_id: str, client_secret: str) -> str:
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
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token(request: Request = None, client_id: str="", client_secret: str=""):
    # for swagger
    if not client_id:
        data = await request.form()
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")

    return get_access_token(client_id, client_secret)


def _get_current_client(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id: str = payload.get("sub")
        scopes: List[str] = payload.get("scopes", [])

        if client_id is None or _get_client_by_id(client_id) is None:
            raise credentials_exception

        token_data = TokenData(client_id=client_id, scopes=scopes)
    except JWTError:
        raise credentials_exception

    return token_data


async def get_current_api_client(token: str = Depends(oauth2_scheme)) -> TokenData:
    return _get_current_client(token)


async def get_current_web_client(request: Request) -> TokenData:
    token = request.cookies.get("access_token")
    return _get_current_client(token)
