"""
URL configuration for eventz_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

# eventz_project/urls.py

from django.contrib import admin
from django.urls import path, include
from events import views  # we'll put our view functions in events/views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth-related paths:
    path('accounts/', include('django.contrib.auth.urls')), 
    # The above line includes default auth routes: login/ logout/ password_reset/ etc.
    # It expects templates under registration/ directory by default for login and password management.

    # Signup URLs
    path('signup/', views.signup, name='signup'),  # user signup
    path('signup/organizer/', views.organizer_signup, name='organizer_signup'),

    # Event app URLs (we will add more as we implement events)
    path('', include('events.urls')),  # include events app URLs (to create separately)
]
