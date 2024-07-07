from fastapi import Depends

from app.sec.security import router, get_current_api_client, get_current_web_client, TokenData, get_access_token, \
    are_valid_scopes

GET_CURRENT_API_CLIENT = Depends(get_current_api_client)
GET_CURRENT_WEB_CLIENT = Depends(get_current_web_client)
