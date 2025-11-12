import hashlib
from unittest.mock import MagicMock
import pytest
import warnings
from pydantic import PydanticDeprecatedSince20

warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
from django.db import connection
from users.models import Users as User
from users.service import UserServices
from django.utils import timezone
from core.exception.business_exception import BusinessException
from core.config import ProjectConfig
from django.http import HttpRequest

config = ProjectConfig()  # type: ignore

USER_LOGIN_STATE = config.user_login_state
SALT = config.salt


@pytest.mark.django_db(transaction=False)  # 必须禁用事务
def test_unmanaged_model():
    # 测试基础查询
    count = User.objects.count()
    print(f"实际用户数: {count}")
    assert count >= 0

    print(f"\n实际用户数（开发数据库）: {count}")
    assert count >= 0  # 基础验证


@pytest.mark.django_db(transaction=False)  # 允许数据库访问
def test_create_user():
    # 创建 User 对象
    user = User.objects.create(
        user_name="john_doe",
        user_account="john123",
        avatar_url="http://example.com/avatar.jpg",
        gender=1,
        user_password="password123",
        phone="123456789",
        email="john.doe@example.com",
        user_status=1,
        create_time=timezone.now(),
        update_time=timezone.now(),
        is_delete=0,
        user_role=0,
        planet_code="earth",
        tags="学生",
    )
    user_id = user.pk
    print(f"user_id : {user_id}")
    assert user_id


@pytest.mark.django_db(transaction=False)
def test_user_register():
    user_service = UserServices()

    # 测试参数为空
    with pytest.raises(BusinessException) as exc:
        user_service.user_register("", "", "", "")
    assert exc.value.description == "参数为空"

    # 测试用户账号过短
    with pytest.raises(BusinessException) as exc:
        user_service.user_register("abc", "password123", "password123", "12345")
    assert exc.value.description == "用户账号过短"

    # 测试用户密码过短
    with pytest.raises(BusinessException) as exc:
        user_service.user_register("valid12", "short", "short", "12345")
    assert exc.value.description == "用户密码过短"

    # 测试星球编号过长
    with pytest.raises(BusinessException) as exc:
        user_service.user_register("valid12", "password123", "password123", "123456")
    assert exc.value.description == "星球编号过长"

    # 测试用户名含特殊字符
    with pytest.raises(BusinessException) as exc:
        user_service.user_register("invalid@", "password123", "password123", "12345")
    assert exc.value.description == "用户名含特殊字符"

    # 测试密码和校验密码不一致
    with pytest.raises(BusinessException) as exc:
        user_service.user_register("valid12", "password123", "different", "12345")
    assert exc.value.description == "密码和校验密码不一致"

    # 测试重复用户名
    User.objects.create(
        user_account="existing",
        user_password="pwd",
        planet_code="123",
        user_status=0,
        is_delete=0,
        user_role=0,
    )
    with pytest.raises(BusinessException) as exc:
        user_service.user_register("existing", "password123", "password123", "12345")
    assert exc.value.description == "重复用户名"

    # 测试重复星球编号
    User.objects.create(
        user_account="newuser",
        user_password="pwd",
        planet_code="12345",
        user_status=0,
        is_delete=0,
        user_role=0,
    )
    with pytest.raises(BusinessException) as exc:
        user_service.user_register("another", "password123", "password123", "12345")
    assert exc.value.description == "重复星球编号"

    # 测试成功注册
    user_id = user_service.user_register(
        user_account="newuser123",
        user_password="password123",
        check_password="password123",
        planet_code="54321",
    )
    assert user_id > 0
    assert User.objects.filter(id=user_id).exists()


@pytest.mark.django_db(transaction=False)
def test_do_login():
    user_service = UserServices()
    mock_request = MagicMock(spec=HttpRequest)
    mock_request.session = {"user_login_state": ""}  # 添加session属性

    # 创建测试用户
    test_user = User.objects.create(
        user_name="Test User",
        user_account="testuser",
        avatar_url="http://example.com/avatar.jpg",
        gender=1,
        user_password=hashlib.md5((SALT + "password123").encode("utf-8")).hexdigest(),
        phone="123456789",
        email="john.doe@example.com",
        user_status=1,
        create_time=timezone.now(),
        update_time=timezone.now(),
        is_delete=0,
        user_role=0,
        planet_code="earth",
        tags="学生",
    )

    # 测试参数为空
    with pytest.raises(BusinessException) as exc:
        user_service.do_login(mock_request, "", "")
    assert exc.value.description == "参数为空"

    # 测试用户账号过短
    with pytest.raises(BusinessException) as exc:
        user_service.do_login(mock_request, "abc", "password123")
    assert exc.value.description == "用户账户过短"

    # 测试用户密码过短
    with pytest.raises(BusinessException) as exc:
        user_service.do_login(mock_request, "testuser", "short")
    assert exc.value.description == "用户密码过短"

    # 测试用户名含特殊字符
    with pytest.raises(BusinessException) as exc:
        user_service.do_login(mock_request, "user@name", "password123")
    assert exc.value.description == "用户名不允许含有特殊字符"

    # 测试密码错误
    with pytest.raises(BusinessException) as exc:
        user_service.do_login(mock_request, "testuser", "wrongpassword")
    assert exc.value.description == "密码输入错误"

    # 测试成功登录
    result = user_service.do_login(mock_request, "testuser", "password123")
    assert result is not None
    assert result.user_account == "testuser"
    assert result.user_id == test_user.id


@pytest.mark.django_db(transaction=False)
def test_do_logout():
    user_service = UserServices()
    mock_request = MagicMock(spec=HttpRequest)

    # 创建完整的MagicMock session对象
    mock_session = MagicMock()
    mock_request.session = mock_session

    # 测试正常登出
    mock_session.__contains__.return_value = True  # 模拟有登录状态
    result = user_service.do_logout(mock_request)
    assert result == 1
    mock_session.flush.assert_called_once()

    # 测试重复登出
    mock_session.__contains__.return_value = False  # 模拟无登录状态
    with pytest.raises(BusinessException) as exc:
        user_service.do_logout(mock_request)
    assert exc.value.description == "用户已登出"
    mock_session.flush.assert_called()
