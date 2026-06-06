from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging
from fastapi.responses import JSONResponse

# 获取 Uvicorn 的访问日志记录器
logger = logging.getLogger('uvicorn.access')
logger.disabled = True

def register_middleware(app: FastAPI):
    
    @app.middleware("http")
    # call_next 是一个函数，用于调用下一个中间件或路由处理函数
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time()-start_time
        '''
        格式化一条 HTTP 请求日志消息。
        各字段含义：
        
        - request.client.host — 客户端 IP 地址
        - request.client.port — 客户端端口
        - request.method — HTTP 请求方法（GET、POST 等）
        - request.url.path — 请求的 URL 路径
        - response.status_code — 响应状态码（200、404、500 等）
        - processing_time — 处理该请求所花费的时间（秒）
        '''
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else 0
        message = f"{client_host}: {client_port} - {request.method} - {request.url.path} - {response.status_code} - completed after {processing_time}s"
        print(message)
        return response
    
    # 允许所有来源的 CORS 请求
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True
    )
    
    # 允许所有主机名
    app.add_middleware(
        TrustedHostMiddleware,
        # 此处填写允许的主机名
        allowed_hosts=["localhost", "127.0.0.1"]
    )
    
    # async def authrization(request: Request, call_next):
    #     if not "Authorization" in request.headers:
    #         return JSONResponse(
    #             content={"detail": "Authorization header is missing", "resolution": "Add Authorization header"},
    #             status_code=status.HTTP_401_UNAUTHORIZED
    #         )
    #     response = await call_next(request)
    #     return response
