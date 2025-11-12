# 数据校验层
from ninja import Schema
from typing import Optional, Any, Type, TypeVar
from pydantic.alias_generators import to_camel, to_snake
from pydantic import ConfigDict
from core.constants import ErrorCode
from core.types import ExceptionResponse

# 定义类型变量，限定为ResponseBase及其子类
T = TypeVar("T", bound="ResponseBase")


class ResponseBase(Schema):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    code: Optional[int]
    data: Any
    message: Optional[str]
    description: Optional[str]

    @classmethod
    def success(cls: Type[T], data: Any, description: str = "") -> T:
        return cls(code=0, data=data, message="ok", description=description)

    @staticmethod
    def from_error_code(
        code: Optional[int] = 00000,
        description: Optional[str] = "",
        message: Optional[str] = "",
        error_code: Optional[ErrorCode] = None,
    ) -> ExceptionResponse:
        if error_code != None:
            return {
                "code": error_code.code,
                "message": error_code.message,
                "description": error_code.description,
            }

        return {"code": code, "message": message, "description": description}
