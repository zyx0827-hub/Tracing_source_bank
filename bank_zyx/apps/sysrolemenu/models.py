from django.db import models


class SysRoleMenu(models.Model):
    role_id = models.IntegerField()
    menu_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sys_role_menu'