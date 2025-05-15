from django.shortcuts import render

# events/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from .forms import SignUpForm

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

