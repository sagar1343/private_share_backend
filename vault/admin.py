from django.contrib import admin

from .models import PrivateFile, Collection, Recipient, AccessLog


# Register your models here.
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "created_at", "file_count"]

    @admin.display(description="File count")
    def file_count(self, obj):
        return obj.privatefile_set.count()


@admin.register(PrivateFile)
class PrivateFileAdmin(admin.ModelAdmin):
    list_display = ["file_name", "created_at", "max_download_count", "download_count", "expiration_time", "logs_count"]
    
    @admin.display(description="Logs")
    def logs_count(self, obj):
        return obj.accesslog_set.count()


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ["user", "permission_type", "private_file"]


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ["user", "private_file", "access_time"]
