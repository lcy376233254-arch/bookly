from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.reviews.schemas import ReviewCreateModel
from fastapi.exceptions import HTTPException
from fastapi import status
import logging

book_service = BookService()
user_service = UserService()

class ReviewService:
    
    async def add_review_to_book(self,user_email:str, book_uid:str,review_data: ReviewCreateModel,session: AsyncSession):
        try:
            book = await book_service.get_book(book_uid,session=session)
            user = await user_service.get_user_by_email(user_email,session=session)
            review_data_dict = review_data.dict()
            new_review = Review(
                **review_data_dict
            )
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="书籍不存在")
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
            new_review.user = user
            new_review.book = book
            session.add(new_review)
            await session.commit()
            return new_review
        except Exception as e:
            logging.error(f"添加评论失败: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="出错了")
