from django.db import models

# Create your models here.
class SysMenu(models.Model):
    menu_id = models.AutoField(primary_key=True, db_comment='菜单id')
    menu_name = models.CharField(max_length=50, db_comment='菜单名称')
    menu_url = models.CharField(max_length=200, blank=True, null=True, db_comment='菜单链接')
    parent_id = models.IntegerField(blank=True, null=True, db_comment='父级菜单ID')
    sort_order = models.IntegerField(db_comment='排序顺序')
    remark = models.CharField(max_length=200, blank=True, null=True, db_comment='备注')

    class Meta:
        managed = False
        db_table = 'sys_menu'
        db_table_comment = '菜单信息表'