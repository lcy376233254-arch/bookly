from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from src.auth.utils import decode_token
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from .service import UserService
from typing import Any, List
from src.db.models import User
from src.error import InvalidToken, RevokedToken, AccessTokenRequired, RefreshTokenRequired, UserAlreadyExists, InsufficientPermission,AccountNotVerified

user_service = UserService()



# 定义一个类 AccessTokenBearer ，继承自 FastAPI 的 HTTPBearer 安全方案类，用于处理 Bearer Token 认证。
class TokenBearer(HTTPBearer):
    # 构造函数， auto_error=True 表示认证失败时自动抛出 403 错误。
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self,request: Request) -> HTTPAuthorizationCredentials | None:

        creds = await super().__call__(request=request)
        token = creds.credentials
        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()
        if await token_in_blocklist(token_data['jti']):
            raise InvalidToken()
        self.verify_token_data(token_data)
        return token_data
    def token_valid(self,token: str) -> bool:
        return decode_token(token) is not None

    def verify_token_data(self,token_data):
        raise NotImplementedError('Subclasses must implement verify_token_data')

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self,token_data: dict) -> None:
        if token_data and token_data['refresh']:
            raise AccessTokenRequired()

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self,token_data: dict) -> None:
        if token_data and not token_data['refresh']:
            raise RefreshTokenRequired()
        
async def get_current_user(token_details:dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_details['user']['email']
    user = await user_service.get_user_by_email(user_email, session)
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()
