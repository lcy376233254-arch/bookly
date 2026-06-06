from celery import Celery
from src.mail import create_message,mail
from asgiref.sync import async_to_sync

c_app = Celery()

c_app.config_from_object('src.books.config')
# celery实现后台任务
@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)
    # 将发送邮件消息的异步代码转换为同步代码
    async_to_sync(mail.send_message)(message)

    print("邮件已发送！")