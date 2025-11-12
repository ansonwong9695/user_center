from typing import Optional
from core.constants import ErrorCode


class BusinessException(Exception):

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[int] = None,
        description: Optional[str] = None,
        error_code: Optional[ErrorCode] = None,
    ) -> None:
        """
        初始化业务异常

        参数:
            message: 错误信息
            code: 错误码
            description: 错误描述
            error_code: 错误码枚举值
        """
        if error_code is not None:
            super().__init__(error_code.message)
            self.code = error_code.code
            self.message = error_code.message
            self.description = description
        else:
            super().__init__(message)
            self.code = code
            self.message = message
            self.description = description

    def __str__(self):
        return f"[{self.code}] {super().__str__()}: {self.description}"
