from enum import Enum


class ErrorCode(Enum):
    # 成功
    SUCCESS = (0, "ok", "")
    # 通用错误
    PARAMS_ERROR = (40000, "请求参数错误", "")
    NULL_ERROR = (40001, "请求数据为空", "")
    NOT_LOGIN = (40100, "未登录", "")
    NO_AUTH = (40101, "无权限", "")
    USER_NOT_EXIST = (40102, "密码不正确", "")
    ALREADY_LOGOUT = (40300, "已经登出", "")
    SYSTEM_ERROR = (50000, "系统内部异常", "")

    def __init__(self, code: int, message: str, description: str):
        self.code = code
        self.message = message
        self.description = description
