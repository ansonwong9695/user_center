from ninja import NinjaAPI
from users.api import router as user_router
from users.schemas import ResponseBase
import logging
from core.constants import ErrorCode
from core.exception_handler import exception_handler


logger = logging.getLogger("django")
api = NinjaAPI(title="UserCenter API", version="1.0.0")

# 挂载子路由
api.add_router("users/", user_router)


# 注册异常处理器
exception_handler(api)
