from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.
class Announcements(models.Model):
    title = models.CharField(max_length=200, db_comment='公告标题')
    content = models.TextField(db_comment='公告内容')
    
    # 新增：详情附件字段
    detail_attachment = models.CharField(
        max_length=500, 
        null=True, 
        blank=True, 
        db_comment='详情附件路径（Word/PDF）'
    )
    
    publisher_id = models.CharField(max_length=11, db_comment='发布人ID')
    publish_time = models.DateTimeField(blank=True, null=True, db_comment='发布时间')
    status = models.IntegerField(blank=True, null=True, db_comment='状态：1-正常，0-删除')

    class Meta:
        managed = False
        db_table = 'announcements'
        db_table_comment = '公告信息表'
    
    # 新增：自定义方法，用于获取附件状态
    @property
    def has_attachment(self):
        """判断是否有附件"""
        return bool(self.detail_attachment)
    
    @property
    def attachment_extension(self):
        """获取附件文件扩展名"""
        if self.detail_attachment:
            import os
            return os.path.splitext(self.detail_attachment)[1].lower()
        return None
    
    @property
    def is_pdf_attachment(self):
        """判断是否是PDF附件"""
        return self.attachment_extension == '.pdf'
    
    @property
    def is_word_attachment(self):
        """判断是否是Word附件"""
        return self.attachment_extension in ['.doc', '.docx']
    
    # 状态常量（可选，方便使用）
    STATUS_NORMAL = 1
    STATUS_DELETED = 0
    
    def is_normal(self):
        """是否正常状态"""
        return self.status == self.STATUS_NORMAL
    
    def is_deleted(self):
        """是否已删除"""
        return self.status == self.STATUS_DELETED