from django.contrib import admin

from notifications.models import Notification


pk = 'pk'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface configuration for the Notification model."""

    list_display = (pk, 'type', 'status', 'user')
    list_display_links = list_display
    search_fields = list_display
    list_filter = ('type', 'status')
    ordering = ('created_at',)
