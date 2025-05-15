from django.contrib import admin
from .models import Category, Event, Ticket

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'location', 'organizer', 'capacity', 'tickets_sold')
    list_filter = ('category', 'start_time', 'organizer')
    search_fields = ('title', 'description', 'location')

    def tickets_sold(self, obj):
        return obj.tickets.count()
    tickets_sold.short_description = "Tickets Sold"

admin.site.register(Category)
admin.site.register(Event, EventAdmin)
admin.site.register(Ticket)
