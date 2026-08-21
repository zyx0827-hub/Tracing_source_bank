from django.db import models
from django.db import models


class SysUserRole(models.Model):
    user_id = models.IntegerField()
    role_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sys_user_role'