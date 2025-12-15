from django.contrib import admin
from .models import MediaJob


@admin.register(MediaJob)
class MediaJobAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'file_name',
        'size',
        'attempts',
        'created_at',
    )
    list_filter = ('status',)
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'attempts',
        'error',
        'result',
    )
