from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, OutputWrapper
from django.core.management.color import Style
from django.db.models import QuerySet


DEFAULT_ADMIN_USERNAME = 'test_admin'
DEFAULT_ADMIN_EMAIL = 'test_admin@test.com'
DEFAULT_ADMIN_PASSWORD = 'test_admin_pass'  # noqa: S105

DEFAULT_ORGANIZER_USERNAMES = ('test_organizer_1', 'test_organizer_2')
DEFAULT_VISITOR_USERNAMES = ('test_visitor_1', 'test_visitor_2')


def get_or_create_default_admin(
    output: OutputWrapper,
    style: Style,
) -> User:
    user_admin, created = User.objects.get_or_create(
        username=DEFAULT_ADMIN_USERNAME
    )
    if created:
        user_admin.set_password(DEFAULT_ADMIN_PASSWORD)
        user_admin.email = DEFAULT_ADMIN_EMAIL
        user_admin.is_staff = True
        user_admin.is_superuser = True
        user_admin.save()
        output.write(style.SUCCESS('Superuser created!'))
    else:
        output.write(style.NOTICE('Superuser already exists.'))
    return user_admin


def get_or_create_default_organizers(
    output: OutputWrapper,
    style: Style,
) -> QuerySet[User]:
    for username in DEFAULT_ORGANIZER_USERNAMES:
        organizer, created = User.objects.get_or_create(
            username=username,
            is_staff=True,
        )
        if created:
            organizer.set_password(f'{username}_pass')
            organizer.save()
            output.write(style.SUCCESS(f'Organizer {username}: created!'))
        else:
            output.write(style.NOTICE(f'Organizer {username}: exists!'))
    return User.objects.filter(username__in=DEFAULT_ORGANIZER_USERNAMES)


def get_or_create_default_visitors(
    output: OutputWrapper,
    style: Style,
) -> QuerySet[User]:
    for username in DEFAULT_VISITOR_USERNAMES:
        visitor, created = User.objects.get_or_create(username=username)
        if created:
            visitor.set_password(f'{username}_pass')
            visitor.save()
            output.write(style.SUCCESS(f'Visitor {username}: created!'))
        else:
            output.write(style.NOTICE(f'Visitor {username}: exists!'))
    return User.objects.filter(username__in=DEFAULT_ORGANIZER_USERNAMES)


class Command(BaseCommand):
    """TODO."""

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: WPS110,WPS210
        """TODO."""
        get_or_create_default_admin(self.stdout, self.style)
        get_or_create_default_organizers(self.stdout, self.style)
        get_or_create_default_visitors(self.stdout, self.style)

        for group, filters in {
            'admins': {'is_superuser': True},
            'organizers': {'is_staff': True},
            'visitors': {'is_staff': False},
        }.items():
            users = User.objects.filter(**filters)
            self.stdout.write(self.style.SUCCESS(f'{group}: {users}'))
