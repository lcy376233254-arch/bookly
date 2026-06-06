from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from src.books.config import Config
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

JWT_SECRET = Config.JWT_SECRET
JWT_ALGORITHM = Config.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRY = 3600

# 使用 argon2 算法，没有 72 字节限制
passwd_context = CryptContext(schemes=['argon2'])

def generate_passwd_hash(password: str) -> str:
    hash = passwd_context.hash(password)
    return hash

def verify_passwd(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)
# 创建 JWT 访问令牌
def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}

    payload['user'] = user_data
    if expiry is not None:
        exp_time = datetime.now() + expiry
    else:
        exp_time = datetime.now() + timedelta(days=ACCESS_TOKEN_EXPIRY)
    payload['exp'] = int(exp_time.timestamp())
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload= payload,
        key= JWT_SECRET,
        algorithm= JWT_ALGORITHM
    )
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key= JWT_SECRET,
            algorithms= [JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(f'Invalid token: {e}')
        return None
# 接收JWT密钥和数据
serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET,
    salt="email-configuration"
)
def create_url_safe_token(data:dict):
    # 序列化数据
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token:str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.exception(str(e))
