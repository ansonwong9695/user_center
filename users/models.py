from django.db import models


# 自定义管理器，实现逻辑删除
class ActiveUserManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_delete=0)


# Create your models here.
class Users(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="id")
    user_name = models.CharField(
        max_length=256, blank=True, null=True, db_comment="用户昵称"
    )
    user_account = models.CharField(
        max_length=256, blank=True, null=True, db_comment="账号"
    )
    avatar_url = models.CharField(
        max_length=1024, blank=True, null=True, db_comment="用户头像"
    )
    gender = models.IntegerField(blank=True, null=True, db_comment="性别")
    user_password = models.CharField(max_length=512, db_comment="密码")
    phone = models.CharField(max_length=128, blank=True, null=True, db_comment="电话")
    email = models.CharField(max_length=512, blank=True, null=True, db_comment="邮箱")
    user_status = models.IntegerField(db_comment="状态 0-正常")
    create_time = models.DateTimeField(blank=True, null=True, db_comment="创建时间")
    update_time = models.DateTimeField(blank=True, null=True, db_comment="更新时间")
    is_delete = models.IntegerField(db_comment="是否删除")
    user_role = models.IntegerField(db_comment="用户角色 0-普通用户 1-管理员")
    planet_code = models.CharField(
        max_length=512, blank=True, null=True, db_comment="星球编号"
    )
    tags = models.CharField(
        max_length=1024, blank=True, null=True, db_comment="标签列表"
    )
    # 添加自定义管理器
    objects = ActiveUserManager()  # 默认只返回未删除用户
    all_objects = models.Manager()  # 原始管理器

    class Meta:
        managed = False
        db_table = "users"
        db_table_comment = "用户"
