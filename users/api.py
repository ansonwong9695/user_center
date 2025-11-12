from ninja import Router, Schema
from .service import UserServices
from typing import Optional, Union, List, Dict
from .schemas import (
    UserLoginRequest,
    UserRegisterRequest,
    UserLoginResponse,
    UserRegisterResponse,
    DeleteResponse,
    SearchResponse,
)  # 导入请求和响应类，作为数据校验层
from core.config import ProjectConfig


router = Router()
user_service = UserServices()
config = ProjectConfig()  # type: ignore


# 通过装饰器指定了响应格式
@router.post("/register", response=Union[UserRegisterResponse, int], by_alias=True)
def user_register(request, data: UserRegisterRequest):  # 通过传参定义了请求体
    # 这里不做data 是否为 none 的判断
    # 因为框架 shcema 部分会进行判断，如果确实直接返回错误
    user_account = data.user_account
    user_password = data.user_password
    check_password = data.check_password
    planet_code = data.planet_code
    # 注册
    user_id = user_service.user_register(
        user_account, user_password, check_password, planet_code
    )
    result = {"user_id": user_id} if user_id != -1 else -1

    return UserRegisterResponse.success(result)


@router.post("/login", response=UserLoginResponse, by_alias=True)
def user_login(request, data: UserLoginRequest) -> UserLoginResponse:
    user_account = data.user_account
    user_password = data.user_password
    user = user_service.do_login(
        request,
        user_account,
        user_password,
    )

    return UserLoginResponse.success(user)


@router.post("/logout", response=int)
def user_logout(request) -> int:
    return user_service.do_logout(request)


@router.get("/search", response=SearchResponse)
def search_user(request, user_name: Optional[str] = None) -> SearchResponse:
    # 1.鉴权
    if not is_admin(request):
        return SearchResponse.success([])
    # 2.查询符合要求的用户
    users = UserServices.list(user_name)

    return SearchResponse.success(users)


@router.get("/delete", response=DeleteResponse)
def delete_user(request, user_id: int) -> DeleteResponse:
    # 1. 鉴权
    if not is_admin(request):
        return DeleteResponse.success({"response": False})
    # 2. 数据校验，确保有效id
    if user_id <= 0:
        return DeleteResponse.success({"response": False})
    # 3. 删除用户
    data = {"response": UserServices.delete_user(user_id)}
    return DeleteResponse.success(data)


def is_admin(request):
    # 这里 Django，会自动从前端发来的请求中的，
    # cookie 找到 session_id,再到数据库中找到匹配session_id
    # 对应的用户数据,返回给我们
    try:
        safety_user = request.session[config.user_login_state]
    except KeyError:
        safety_user = None

    # 判断用户是否登录，以及是否为管理员
    if safety_user == None or safety_user["user_role"] != config.admin_role:
        return False

    return True
