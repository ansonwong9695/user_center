"""
用户服务实现类
"""

from .models import Users as User
from django.forms.models import model_to_dict
from django.contrib.auth import logout
from django.utils import timezone
from core.config import ProjectConfig
from django.http import HttpRequest
from typing import Optional, Union, TypedDict, List
from .schemas import SafetyUser
from core.exception.business_exception import BusinessException
from core.constants import ErrorCode
import re
import hashlib
import logging
import math

config = ProjectConfig()  # type: ignore
logger = logging.getLogger("django")
SALT = config.salt
USER_LOGIN_STATE = config.user_login_state


class UserServices:

    @staticmethod
    def user_register(
        user_account: str,
        user_password: str,
        check_password: str,
        planet_code: str,
        user_status: int = 0,
    ) -> int:
        """用户注册服务
        Args:
            user_account: 用户账号(4位以上字母数字组合)
            user_password: 用户密码(至少8位)
            check_password: 确认密码(需与user_password一致)
            planet_code: 星球编号
            user_status: 用户状态
        Returns:
            int: 成功返回用户ID，失败返回-1
        """
        # 1. 校验
        # 1.1 校验符合长度，不为空
        if not all([user_account, user_password, check_password, planet_code]):
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="参数为空"
            )

        if len(user_account) < 4:
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="用户账号过短"
            )

        if len(user_password) < 8 or len(check_password) < 8:
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="用户密码过短"
            )

        if len(planet_code) > 5:
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="星球编号过长"
            )

        # 1.2 账户不能包含特殊字符
        valid_pattern = r"[^a-zA-Z0-9]"
        if re.search(valid_pattern, user_account):
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="用户名含特殊字符"
            )

        # 1.3 密码和校验密码相同
        if not user_password == check_password:
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="密码和校验密码不一致"
            )

        # 1.4 账户不能重复
        exists = User.objects.filter(user_account=user_account).exists()
        if exists:
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="重复用户名"
            )

        # 1.5 星球编号不能重复
        exists = User.objects.filter(planet_code=planet_code).exists()
        if exists:
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="重复星球编号"
            )

        # 2. 加密
        md5 = hashlib.md5()
        salt_pass = SALT + user_password
        md5.update(salt_pass.encode("utf-8"))
        encrypt_password = md5.hexdigest()

        # 3. 插入数据
        user = User()
        user.user_account = user_account
        user.user_password = encrypt_password
        user.user_status = user_status or 0
        user.is_delete = 0
        user.user_role = 0
        user.planet_code = planet_code
        user.create_time = timezone.now()
        user.update_time = timezone.now()
        user.save()

        if user.id:
            return user.id
        else:
            return -1

    @staticmethod
    def do_login(
        request: HttpRequest,
        user_account: str,
        user_password: str,
    ) -> Optional[SafetyUser]:
        """用户登录服务
        Args:
            request: Django HttpRequest对象，用于存储session
            user_account: 用户账号(4位以上字母数字组合)
            user_password: 用户密码(至少8位)

        Returns:
            Optional[dict]: 返回脱敏后的用户数据字典，包含以下字段:
                - user_account: 账号
                - user_name: 用户名
                - user_id: 用户ID
                - avatar_url: 头像URL(可选)
                - gender: 性别(可选)
                - phone: 电话(可选)
                - email: 邮箱(可选)
                - user_status: 账户状态
                - user_role: 用户角色
                - planet_code: 星球编号
            如果登录失败返回None
        """
        # 1. 校验
        if not all([user_account, user_password]):
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="参数为空"
            )

        if len(user_account) < 4:
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="用户账户过短"
            )

        if len(user_password) < 8:
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR, description="用户密码过短"
            )

        # 账户不能包含特殊字符
        valid_pattern = r"[^a-zA-Z0-9]"
        if re.search(valid_pattern, user_account):
            raise BusinessException(
                error_code=ErrorCode.PARAMS_ERROR,
                description="用户名不允许含有特殊字符",
            )

        # 2.校验密码和数据库中的密文对比
        # 加密
        md5 = hashlib.md5()
        salt_pass = (SALT + user_password).encode("utf8")
        md5.update(salt_pass)
        encrypt_password = md5.hexdigest()

        # 检测用户在数据库中存不存在
        if not User.objects.filter(
            user_account=user_account, user_password=encrypt_password
        ).exists():
            logger.info("user login failed user account can't match with user password")
            raise BusinessException(
                error_code=ErrorCode.USER_NOT_EXIST, description="密码输入错误"
            )
        user = User.objects.get(
            user_account=user_account, user_password=encrypt_password
        )

        # 3. 用户数据脱敏
        safety_user = UserServices.convert_safety_user(user)

        # 4.记录用户登入状态
        if request != None:
            request.session["USER_LOGIN_STATE"] = safety_user

        return safety_user  # type: SafetyUser

    @staticmethod
    def do_logout(request: HttpRequest) -> int:
        """用户登出
        Args:
            request: Django HttpRequest对象，用于存储session
        Returns:
            int: 1 表示登出
        """
        if hasattr(request, "session") and USER_LOGIN_STATE in request.session:
            request.session.flush()
            return 1

        request.session.flush()
        raise BusinessException(
            error_code=ErrorCode.ALREADY_LOGOUT, description="用户已登出"
        )

    @staticmethod
    def list(user_name: Optional[str]) -> List[Optional[SafetyUser]]:
        """
        根据用户名模糊查询用户列表
        Args:
            user_name: 要查询的用户名(支持模糊匹配)
        Returns:
            List[SafetyUser]: 脱敏后的用户信息列表，可能为空列表
        """
        # 1.检查是否为None或纯空格
        if not user_name or user_name.isspace():
            # 1.1. 如果纯空，获取所以用户信息
            users = User.objects.all()
        else:
            # 2. 查询符合条件的
            users = User.objects.filter(user_name__icontains=user_name)  #

        # 3. 数据脱敏
        return [UserServices.convert_safety_user(user) for user in users]

    @staticmethod
    def delete_user(user_id) -> bool:
        try:
            return User.objects.get(id=user_id).delete()[0] > 0
        except User.DoesNotExist:
            logger.warning(f"尝试删除不存在的用户ID: {user_id}")
            return False

    @staticmethod
    def convert_safety_user(user: User) -> Optional[SafetyUser]:
        if user is None:
            return None
        # 1.数据脱敏, 创建一个字典，把可以传给数据层的数据，放进去，以便于数据层读取
        return SafetyUser(
            user_account=user.user_account or "",
            user_name=user.user_name or "",
            user_id=user.id,
            avatar_url=user.avatar_url,
            gender=user.gender,
            phone=user.phone,
            email=user.email,
            user_status=user.user_status,
            user_role=user.user_role,
            planet_code=user.planet_code or "",
        )
