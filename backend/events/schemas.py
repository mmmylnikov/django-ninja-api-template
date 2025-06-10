from datetime import date, datetime
from typing import Annotated

from django.contrib.postgres.search import SearchRank, SearchVector
from django.db.models import QuerySet
from ninja import FilterSchema, ModelSchema, Schema
from pydantic import AfterValidator, Field

from events.models import Booking, Event, EventStatus


class EventFilterSchema(FilterSchema):
    """Filter Schema for defining Event filtering parameters."""

    city: str | None = Field(  # type: ignore
        default=None,
        q='city__icontains',
        example='Moscow',
    )
    status: EventStatus | None = Field(  # type: ignore
        default=None,
        example=EventStatus.UPCOMING.value,
    )
    start_date: date | None = Field(  # type: ignore
        default=None,
        q='start_time__date',
        example='2025-06-16',
    )
    available_for_booking: bool | None = Field(
        default=None,
    )
    description: str | None = Field(
        default=None,
    )

    def filter(self, queryset: QuerySet) -> QuerySet:  # type: ignore
        if self.available_for_booking is not None:
            available_for_booking_check = self.available_for_booking
            self.available_for_booking = None  # noqa: WPS601
            if available_for_booking_check:
                queryset = queryset.filter(_seats_available__gte=1)
            else:
                queryset = queryset.filter(_seats_available=0)
        if self.description is not None:
            description_query = self.description
            self.description = None  # noqa: WPS601
            if description_query:
                queryset = (
                    queryset.annotate(
                        search=SearchVector('description'),
                        rank=SearchRank(
                            vector=SearchVector('description'),
                            query=description_query,
                        ),
                    )
                    .filter(search=description_query)
                    .order_by('-rank')
                )
        return super().filter(queryset)


class EventIn(Schema):
    title: str
    description: str
    start_time: datetime
    city: str
    seats_total: Annotated[int, Field(gt=0)]


class EventOut(ModelSchema):
    seats_booked: int = 0
    seats_available: int = 0

    class Meta:
        model = Event
        fields = (
            'id',
            'title',
            'description',
            'start_time',
            'city',
            'seats_total',
            'status',
            'organizer',
        )


def validate_status(status: str) -> str:
    if status not in EventStatus:
        raise ValueError(f'The status should be one of: {EventStatus.values}')
    return status


class EventStatusUpdateIn(Schema):
    status: Annotated[str, AfterValidator(validate_status)]


class CreateBookingIn(Schema):
    seats: int = 1


class BookingOut(ModelSchema):
    class Meta:
        model = Booking
        fields = (
            'id',
            'event',
            'user',
            'seats',
            'attended',
        )
