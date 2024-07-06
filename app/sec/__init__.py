from fastapi import Depends

from .security import router, get_current_api_client, get_current_web_client, TokenData, login_for_access_token

GET_CURRENT_API_CLIENT = Depends(get_current_api_client)
GET_CURRENT_WEB_CLIENT = Depends(get_current_web_client)
