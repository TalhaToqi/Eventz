from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db import transaction
from events.models import Category, Event, Ticket
from datetime import timedelta
import random

class Command(BaseCommand):
    help = "Generate sample data with organizers, events and registrations"

    def add_arguments(self, parser):
        parser.add_argument('--organizers', type=int, default=10, help='Number of organizer accounts to create')
        parser.add_argument('--tickets', type=int, default=50, help='Number of ticket registrations to create')

    @transaction.atomic
    def handle(self, *args, **options):
        num_organizers = options['organizers']
        num_tickets = options['tickets']

        self.stdout.write(self.style.NOTICE('Creating categories...'))
        categories = []
        for name in ['Conference', 'Concert', 'Networking', 'Workshop', 'Seminar']:
            cat, _ = Category.objects.get_or_create(name=name)
            categories.append(cat)

        org_group, _ = Group.objects.get_or_create(name='Organizers')

        self.stdout.write(self.style.NOTICE('Creating organizer users and events...'))
        events = []
        for i in range(num_organizers):
            username = f'organizer{i}'
            if User.objects.filter(username=username).exists():
                organizer = User.objects.get(username=username)
            else:
                organizer = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password')
                organizer.groups.add(org_group)

            start = timezone.now() + timedelta(days=random.randint(1, 30))
            end = start + timedelta(hours=2)
            event = Event.objects.create(
                title=f'Event {i}',
                description='Auto generated event',
                category=random.choice(categories),
                start_time=start,
                end_time=end,
                location=f'Location {i}',
                organizer=organizer,
                price=random.choice([0, 10, 25, 50]),
                capacity=200,
            )
            events.append(event)

        self.stdout.write(self.style.NOTICE('Creating attendee users...'))
        attendees = []
        for i in range(max(num_tickets // 2, 1)):
            username = f'user{i}'
            if User.objects.filter(username=username).exists():
                attendee = User.objects.get(username=username)
            else:
                attendee = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password')
            attendees.append(attendee)

        self.stdout.write(self.style.NOTICE('Creating tickets...'))
        for _ in range(num_tickets):
            Ticket.objects.create(
                event=random.choice(events),
                buyer=random.choice(attendees)
            )

        self.stdout.write(self.style.SUCCESS('Sample data generation complete.'))
