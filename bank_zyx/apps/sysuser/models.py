# apps/sysuser/models.py
from django.db import models

class SysUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    pid = models.CharField(max_length=18)
    email = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=20)
    address = models.CharField(max_length=200, blank=True, null=True)
    password = models.CharField(max_length=255)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sys_user'