from django.contrib import admin

# Register your models here.
from .models import Announcements

@admin.register(Announcements)
class AnnouncementsAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'publisher_id', 'publish_time', 'status', 'has_attachment_display']
    list_filter = ['status', 'publish_time']
    search_fields = ['title', 'content']
    readonly_fields = ['publish_time', 'detail_attachment_display']
    
    fieldsets = [
        ('基本信息', {'fields': ['title', 'content']}),
        ('附件信息', {'fields': ['detail_attachment_display']}),
        ('其他信息', {'fields': ['publisher_id', 'publish_time', 'status']}),
    ]
    
    def has_attachment_display(self, obj):
        return '有' if obj.detail_attachment else '无'
    has_attachment_display.short_description = '是否有附件'
    
    def detail_attachment_display(self, obj):
        if obj.detail_attachment:
            return f'<a href="/api/file/download/{obj.detail_attachment}/" target="_blank">下载附件</a>'
        return '无附件'
    detail_attachment_display.short_description = '附件'
    detail_attachment_display.allow_tags = True