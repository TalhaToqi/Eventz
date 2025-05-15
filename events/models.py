from django.db import models

# events/models.py

from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField("Event Title", max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField("Start Date & Time")
    end_time = models.DateTimeField("End Date & Time", null=True, blank=True)
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                help_text="Ticket price (set 0 for free event)")
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Max tickets available (blank if unlimited)")

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d')}"

class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    purchase_time = models.DateTimeField(auto_now_add=True)
    # For simplicity, a ticket can be represented by this record; 
    # you could add fields like QR code, seat number, etc., if needed.
    # Extended feature fields:
    is_resale = models.BooleanField(default=False, help_text="True if this ticket was resold")
    for_sale = models.BooleanField(default=False, help_text="Ticket put up for resale by owner")
    resale_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                       help_text="Price set for resale (if for_sale=True)")

    def __str__(self):
        return f"Ticket#{self.id} for {self.event.title} ({self.buyer.username})"

