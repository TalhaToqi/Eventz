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
import stripe
from django.conf import settings

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


@login_required
def buy_ticket(request, event_id):
    """Initiate a Stripe Checkout session for the given event."""
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found.")
        return redirect('event_list')

    # If event has capacity and it's sold out, prevent purchase
    if event.capacity and event.tickets.count() >= event.capacity:
        messages.error(request, "This event is sold out.")
        return redirect('event_detail', event_id=event.id)

    # Stripe configuration
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Create a Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        customer_email=request.user.email,  # prefill with user's email
        client_reference_id=request.user.id,  # reference to our user
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f"Ticket for {event.title}",
                },
                'unit_amount': int(event.price * 100) if event.price > 0 else 0,
            },
            'quantity': 1,
        }],
        success_url=request.build_absolute_uri('/') + 'success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/') + f'cancel/?event_id={event.id}',
        metadata={
            'event_id': event.id
        }
    )
    # Redirect to Stripe Checkout
    return redirect(session.url, code=303)

@login_required
def payment_success(request):
    """Handle successful payment - create ticket and thank user."""
    session_id = request.GET.get('session_id')
    if not session_id:
        # If accessed without session (or directly), just redirect home
        return redirect('home')
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        # If session retrieval fails, perhaps log the error (e) and inform user
        messages.error(request, "Unable to verify payment. Please contact support.")
        return redirect('event_list')

    # Double-check payment status
    if session.payment_status == 'paid':
        # Retrieve event id from metadata and user from client_reference_id
        event_id = session.metadata.get('event_id')
        user_id = session.client_reference_id
        if event_id and user_id:
            try:
                event = Event.objects.get(id=event_id)
                user = User.objects.get(id=user_id)
            except (Event.DoesNotExist, User.DoesNotExist):
                messages.warning(request, "Payment received, but event or user not found.")
            else:
                # Create a Ticket
                Ticket.objects.create(event=event, buyer=user)
                messages.success(request, f"Thank you for your purchase! Your ticket for '{event.title}' is confirmed.")
                return redirect('my_tickets')
    # If we reach here, something is off
    messages.error(request, "Payment was not successful. If you believe this is an error, please contact support.")
    return redirect('event_list')

def payment_cancel(request):
    """Handle canceled payment - just inform the user."""
    messages.info(request, "Payment canceled. You have not been charged.")
    return redirect('event_detail', event_id=request.GET.get('event_id', ''))

