from django.db import models


# Create your models here.
class Tags(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="id")
    tag_name = models.CharField(
        unique=True, max_length=256, blank=True, null=True, db_comment="标签名称"
    )
    user_id = models.BigIntegerField(blank=True, null=True, db_comment="用户id")
    parent_id = models.BigIntegerField(blank=True, null=True, db_comment="父标签id")
    is_parent = models.IntegerField(
        blank=True, null=True, db_comment="0-不是，1-父标签"
    )
    create_time = models.DateTimeField(blank=True, null=True, db_comment="创建时间")
    update_time = models.DateTimeField(blank=True, null=True, db_comment="更新时间")
    is_delete = models.IntegerField(db_comment="是否删除")

    class Meta:
        managed = False
        db_table = "tags"
        db_table_comment = "标签"

