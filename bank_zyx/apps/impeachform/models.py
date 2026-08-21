from django.db import models

# Create your models here.
class ImpeachForm(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    name = models.CharField(max_length=50, db_comment='提问人姓名')
    question = models.TextField(db_comment='问题内容')
    create_time = models.DateTimeField(db_comment='提问时间')
    status = models.CharField(max_length=50, db_comment='问题状态')
    process_time = models.DateTimeField(blank=True, null=True, db_comment='首次开始处理的时间')
    answer = models.TextField(blank=True, null=True, db_comment='回答内容（支持长文本/富文本）')
    updated_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.IntegerField(db_comment='逻辑删除标记 0正常 1已删除')

    class Meta:
        managed = False
        db_table = 'impeach_form'