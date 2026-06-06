from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import Optional
from src.books.schemas import BookModel, BookUpdateModel, BookCreateModel,BookDetailModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from src.db.main import get_session
from src.books.service import BookService
from src.db.models import Book
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.error import BookNotFound



book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(['admin', 'user'])


# 获取所有书籍
@book_router.get('/', response_model=List[Book], dependencies=[Depends(role_checker)])
async def get_all_book(session: AsyncSession = Depends(get_session),token_details=Depends(access_token_bearer)):
    books = await book_service.get_all_books(session)
    return books


# 获取某用户所有书籍
@book_router.get('/user/{user_uid}', response_model=List[Book], dependencies=[Depends(role_checker)])
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
):
    books = await book_service.get_user_books(user_uid,session)
    return books


# 创建书籍
@book_router.post('/', status_code = status.HTTP_201_CREATED,response_model=Book, dependencies=[Depends(role_checker)])
async def create_a_book(book_data: BookCreateModel,session: AsyncSession = Depends(get_session),token_details=Depends(access_token_bearer)) -> dict:
    user_id = token_details.get('user')['uid']
    new_book = await book_service.create_book(book_data,user_id,session)
    return new_book


# 获取书籍详情
@book_router.get('/{book_uid}', response_model=BookDetailModel, dependencies=[Depends(role_checker)])
async def get_book(book_uid: str,session: AsyncSession = Depends(get_session),token_details=Depends(access_token_bearer)) -> Optional[dict]:
    book = await book_service.get_book(book_uid,session)
    if book:
        return book
    else:
        # 未找到书籍时，使用HTTPException方法抛出异常，状态码为404，提示信息为Book not found
        # raise HTTPException(status_code=404, detail="Book not found")
        raise BookNotFound()


# 更新书籍
@book_router.patch('/{book_uid}', response_model=Book, dependencies=[Depends(role_checker)])
async def update_book(book_uid: str, bookdata: BookUpdateModel,session: AsyncSession = Depends(get_session),token_details=Depends(access_token_bearer)) -> Optional[dict]:
    update_book = await book_service.update_book(book_uid,bookdata,session)
    if update_book:
        return update_book
    else:
        raise BookNotFound()
    

# 删除书籍
@book_router.delete('/{book_uid}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_checker)])
async def delete_book(book_uid: str,session: AsyncSession = Depends(get_session),token_details=Depends(access_token_bearer)):
    delete_book = await book_service.delete_book(book_uid,session)
    if delete_book is None:
        raise BookNotFound()
    else:
        return {}
