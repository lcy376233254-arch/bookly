from fastapi import FastAPI, Header, status
from fastapi.exceptions import HTTPException
from typing import Optional, List
from src.books.routes import book_router
'''用于数据验证和序列化: BaseModel 是 Pydantic 的核心类，用于：
- 定义数据模型的结构和类型
- 自动验证输入数据是否符合类型要求
- 将 Python 对象序列化为 JSON 格式
- 提供类型提示和 IDE 自动补全支持'''
from src.books.book_data import books
from src.books.schemas import BookModel, BookUpdateModel
# 进入python虚拟环境指令（Windows PowerShell）：.\venv\Scripts\Activate.ps1
# web服务器基础
app = FastAPI()

# 注册书籍路由
app.include_router(book_router, prefix=f"/api/v1/books")
@app.get("/")
async def read_root():
    return {"message": "hello World"}
# # 查询参数
# @app.get('/greet')
# async def greet(name: Optional[str] = 'user',age: Optional[int] = 18) -> dict:
#     return {"message": f"hello {name},you are {age} years old"}
# # 指定请求体的数据类型
# class BookCreateModel(BaseModel):
#     title: str
#     author: str
# @app.post('/create_book')
# async def create_book(bookdata: BookCreateModel):
#     return {
#         "title": bookdata.title,
#         "author": bookdata.author
#     }

# @app.get('/get_headers', status_code=200)
# async def get_headers(
#     accept: str = Header(None),
#     content_type: str = Header(None),
#     user_agent: str = Header(None),
#     host: str = Header(None)
# ):
#     request_headers={}

#     request_headers["Accept"]=accept
#     request_headers["Content-Type"]=content_type
#     request_headers["User-Agent"]=user_agent
#     request_headers["Host"]=host
#     return request_headers

# crud操作



