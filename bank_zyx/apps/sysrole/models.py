from django.db import models

# Create your models here.
class SysRole(models.Model):
    role_id = models.AutoField(primary_key=True, db_comment='角色编号')
    role_name = models.CharField(max_length=50, db_comment='角色名称')
    description = models.CharField(max_length=200, blank=True, null=True, db_comment='描述')

    class Meta:
        managed = False
        db_table = 'sys_role'
        db_table_comment = '角色信息表'