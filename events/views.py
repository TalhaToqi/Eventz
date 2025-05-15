from django.shortcuts import render

# events/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from .forms import SignUpForm
from django.utils import timezone
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.decorators import login_required

def signup(request):
    """Regular user sign-up view."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()       # Create the user
            # (Regular user: no special group assignment)
            login(request, user)     # Log the user in automatically
            messages.success(request, "Account created successfully!")
            return redirect('home')  # redirect to home page (to be defined)
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form, 'is_organizer_signup': False})

def organizer_signup(request):
    """Organizer sign-up view - creates a user and marks them as organizer."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add user to Organizers group
            organizer_group, created = Group.objects.get_or_create(name='Organizers')
            user.groups.add(organizer_group)
            login(request, user)
            messages.success(request, "Organizer account created successfully!")
            return redirect('organizer_dashboard')  # redirect to organizer dashboard (to implement)
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form, 'is_organizer_signup': True})


def home(request):
    """Home page showing a carousel of upcoming events and maybe a search prompt."""
    upcoming_events = Event.objects.filter(start_time__gte=timezone.now()).order_by('start_time')[:5]
    # Get up to 5 upcoming events
    return render(request, 'events/home.html', {'upcoming_events': upcoming_events})


def event_list(request):
    """List all events with optional search and category filtering."""
    events = Event.objects.all().order_by('start_time')
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    show_past = request.GET.get('show_past')

    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        events = events.filter(category_id=category_id)
    else:
        category_id = ''  # for template, to not select any category
    if not show_past:
        # By default, hide past events
        events = events.filter(start_time__gte=timezone.now())
    # If show_past is checked in UI, then we include all events (including past)

    categories = Category.objects.all()
    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': categories,
        'selected_category': category_id,
        'query': query or '',
        'show_past': bool(show_past),
    })

from django.http import Http404
from django.contrib.auth.decorators import login_required

def event_detail(request, event_id):
    """Display details for a specific event, and allow purchasing tickets."""
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404("Event not found")
    # Get existing reviews for the event (extended feature, we'll implement model later)
    reviews = []
    # If we had an EventReview model: reviews = EventReview.objects.filter(event=event)

    return render(request, 'events/event_detail.html', {'event': event, 'reviews': reviews})