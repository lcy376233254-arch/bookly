from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.schemas import UserCreateModel, UserModel, UserLoginModel, UserBooksModel,EmailModel, PasswordResetRequestModel, PasswordResetConfirmModel
from src.auth.service import UserService
from src.db.main import get_session
from .utils import create_access_token, decode_token, verify_passwd,create_url_safe_token,decode_url_safe_token,generate_passwd_hash
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse, HTMLResponse
from src.auth.dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.error import UserAlreadyExists, InvalidCredentials, UserNotFound, InvalidToken
from src.mail import create_message,mail
from src.books.config import Config
from src.celery_tasks import send_email

version = "v1"
auth_router = APIRouter()
user_service = UserService()

# 设定可访问某路由的用户角色
role_checker = RoleChecker(['admin', 'user'])
REFRESH_TOKEN_EXPIRY = 200

@auth_router.post("/send_mail")
async def send_mail(emails:EmailModel):

    emails = emails.addresses
    
    html = """
    <html>
    <head>
        <title>Test Email</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
    </body>
    </html>
    """
    subject = "Welcome!"

    send_email.delay(emails, subject, html)

    return {"message": "Email sent successfully"}

# 注册用户
# @auth_router.post("/signup")
@auth_router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED
)
async def create_user_Account(user_data: UserCreateModel, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()
    
    new_user = await user_service.create_user(user_data, session)
    token = create_url_safe_token({
        "email": email
    })
    
    link = f"http://{Config.DOMAIN}/api/{version}/auth/verify/{token}"
    html_message = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body>
        <h1>Verify your email</h1>
        <p>Please click the link below to verify your email:</p>
        <p><a href="{link}" target="_blank">Verify Email</a></p>
        <p style="font-size:12px; color:#999;">If the button doesn't work, copy and paste this link into your browser:<br>{link}</p>
    </body>
    </html>
    """
    # message = create_message(recipients=[email],subject="Verify your email",body=html_message)
    # # 将发送邮件任务添加到后台任务队列
    # background_tasks.add_task(mail.send_message, message)
    emails = [email]
    subject = "Verify your email"
    send_email.delay(emails, subject, html_message)

    return {
        "message": "Account Created! Check your email for verification link",
        "user":new_user
    }
# 验证用户邮箱
@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(content={"message": "Email verified successfully"}, status_code=status.HTTP_200_OK)
    return JSONResponse(content={"message": "Error occured during verification"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 用户登录
@auth_router.post("/login")
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_passwd(password, user.password)
        if password_valid:
            access_token = create_access_token(
                user_data = {
                    "uid": str(user.uid),
                    "email": user.email,
                    "username": user.username,
                    "role": user.role
                }
            )
            refresh_token = create_access_token(
                user_data = {
                    "uid": str(user.uid),
                    "email": user.email
                },
                refresh = True,
                expiry = timedelta(days=REFRESH_TOKEN_EXPIRY)
            )
            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user":{
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }, 
                status_code=status.HTTP_200_OK
            )
    else:
        raise InvalidCredentials()
# 刷新token
@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data = token_details['user']
        )
        return JSONResponse(content={"message": "Refresh successful", "access_token": new_access_token}, status_code=status.HTTP_200_OK)
    else:
        raise InvalidToken()
    
@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(user= Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@auth_router.get('/logout')
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):

    jti = token_details['jti']
    await add_jti_to_blocklist(jti)
    return JSONResponse(content={"message": "Logout successful"}, status_code=status.HTTP_200_OK)

# 重置密码
'''
1.提供邮件地址->密码重置请求
1.发送重置密码邮件
3.重置密码->确认密码更改
'''

# 请求重置密码
@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email
    token = create_url_safe_token({
        "email": email
    })
    link = f"http://{Config.DOMAIN}/api/{version}/auth/password-reset-confirm/{token}"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body>
        <h1>Reset your password</h1>
        <p>Please click the link below to reset your password:</p>
        <p><a href="{link}" target="_blank">Reset Password</a></p>
        <p style="font-size:12px; color:#999;">If the button doesn't work, copy and paste this link into your browser:<br>{link}</p>
    </body>
    </html>
    """
    
    # message = create_message(recipients=[email],subject="Reset your password",body=html_message)

    # await mail.send_message(message)
    subject = "Reset your password"
    send_email.delay([email], subject, html_message)

    return JSONResponse(content={"message": "Password reset request sent successfully"}, status_code=status.HTTP_200_OK)


# 确认重置密码
@auth_router.post("/password-reset-confirm/{token}")
async def reset_password_confirm(token: str, passwords: PasswordResetConfirmModel, session: AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    confirm_new_password = passwords.confirm_new_password
    
    if new_password != confirm_new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()
        hashed_password = generate_passwd_hash(new_password)
        await user_service.update_user(user, {"password": hashed_password}, session)

        return JSONResponse(content={"message": "Password reset successfully"}, status_code=status.HTTP_200_OK)
    return JSONResponse(content={"message": "Error occured during password reset"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)