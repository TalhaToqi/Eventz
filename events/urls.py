# events/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage (could list events or just welcome)
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/buy/', views.buy_ticket, name='buy_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('organizer/dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('organizer/events/new/', views.create_event, name='create_event'),
    # (We could also have edit event, etc. not shown for brevity)
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]
