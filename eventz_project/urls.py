from django.contrib import admin
from django.urls import path, include
from events import views  # we'll put our view functions in events/views.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth-related paths:
    path('accounts/', include('django.contrib.auth.urls')),

    # Signup URLs
    path('signup/', views.signup, name='signup'),
    path('signup/organizer/', views.organizer_signup, name='organizer_signup'),

    # Event app URLs
    path('', include('events.urls')),
]

# 🚀 Correct: only serve MEDIA in development!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
