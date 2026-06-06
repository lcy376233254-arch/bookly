import email
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from .middleware import register_middleware
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db, get_session
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from src.error import register_all_errors

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Start the server")
    from src.db.models import Book
    # yield之上的语句将在服务器启动时执行
    # yield之下的语句将在服务器关闭时执行
    await init_db()
    yield
    print("End the server")

version = "v1"

app = FastAPI(
    version=version,
    title="Book API",
    description="A simple book API",
    # lifespan=life_span
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    openapi_url=f"/api/{version}/openapi.json",
    contact={
        "email":"26590597444@qq.com"
    }
)

register_all_errors(app)

register_middleware(app)



app.include_router(book_router, prefix=f"/api/{version}/books",tags=["Books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth",tags=['auth'])
app.include_router(review_router, prefix=f"/api/{version}/reviews",tags=['reviews'])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])