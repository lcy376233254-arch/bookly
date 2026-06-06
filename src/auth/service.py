from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import UserCreateModel
from .utils import generate_passwd_hash
from sqlmodel import select

class UserService:
    # 根据邮箱获取用户
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)
        user = result.first()
        return user
    
    # 检查用户是否存在
    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return user is not None
    
    # 创建用户
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(
            **user_data_dict
        )
        new_user.password = generate_passwd_hash(user_data_dict['password'])
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        return new_user
    
    async def update_user(self, user: User,user_data: dict,session: AsyncSession):

        for k, v in user_data.items():
            setattr(user, k, v)
        await session.commit()
        return user