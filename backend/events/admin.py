from typing import Any

from django.contrib import admin
from django.db.models import ForeignKey, QuerySet
from django.forms import ModelChoiceField
from django.http import HttpRequest

from events.models import Booking, Event
from events.services import EventService


pk = 'pk'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface configuration for the Event model."""

    readonly_fields = ('seats_available',)
    list_display = (
        pk,
        'status',
        'start_time',
        'title',
        'seats_total',
        'seats_available',
        'seats_booked',
    )
    list_display_links = list_display
    search_fields = list_display
    list_filter = ('status', 'organizer')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return EventService.get_sorted_events()


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface configuration for the Booking model."""

    list_display = (pk, 'event__title', 'user', 'seats')
    list_display_links = list_display
    search_fields = list_display
    list_filter = ('event', 'user', 'attended')
    ordering = ('created_at',)

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs: Any
    ) -> ModelChoiceField | None:
        if db_field.name == 'event':
            kwargs['queryset'] = EventService.get_booking_available_events()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
