# 数据校验层
from ninja import Schema
from typing import Optional, Any, List, Type, TypeVar
from pydantic.alias_generators import to_camel, to_snake
from pydantic import Field, ConfigDict
from core.constants import ErrorCode
from core.types import ExceptionResponse
from core.schemas import ResponseBase


class SafetyUser(Schema):
    user_account: str
    user_name: str
    user_id: int
    avatar_url: Optional[str]
    gender: Optional[int]
    phone: Optional[str]
    email: Optional[str]
    user_status: int
    user_role: int
    planet_code: str


class RequestBase(Schema):
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)


class ToCamel(Schema):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class UserRegisterRequest(RequestBase):
    user_account: str = Field(..., alias="userAccount")
    user_password: str = Field(..., alias="userPassword")
    check_password: str = Field(..., alias="checkPassword")
    planet_code: str = Field(..., alias="planetCode")


class UserRegisterResponseData(ToCamel):
    user_id: int = Field(..., alias="id")


class UserRegisterResponse(ResponseBase):
    data: UserRegisterResponseData


class UserLoginRequest(RequestBase):
    user_account: str = Field(..., alias="userAccount")
    user_password: str = Field(..., alias="userPassword")


class UserLoginResponseData(ToCamel, SafetyUser):
    user_name: str = Field(..., alias="username")
    user_id: int = Field(..., alias="id")


class UserLoginResponse(ResponseBase):
    data: Optional[UserLoginResponseData]


class DeleteResponseData(ToCamel):
    response: bool


class DeleteResponse(ResponseBase):
    data: DeleteResponseData


class SearchResponse(ResponseBase):
    data: List[UserLoginResponseData]
