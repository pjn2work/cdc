from fastapi import Depends

from app.sec.block_traffic import IPFiltering
from app.sec.security import (
    router,
    cred,
    hash_password,
    are_valid_scopes,
    get_access_token,
    change_client_secret,
    get_current_api_client,
    get_current_web_client,
    TokenData
)

GET_CURRENT_API_CLIENT = Depends(get_current_api_client)
GET_CURRENT_WEB_CLIENT = Depends(get_current_web_client)
