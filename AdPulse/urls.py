import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.views.static import serve
urlpatterns = [

    path('', include('ads.urls')),
    re_path(r'^admin/', admin.site.urls),  # Keep
    path('ads/', include('ads.urls',  namespace='ads')),
    path('accounts/', include('django.contrib.auth.urls')),  # Keep
    path('oauth/', include('social_django.urls', namespace='social')),  # Keep
]

# Serve the static HTML
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urlpatterns += [
    re_path(r'^site/(?P<path>.*)$', serve, name='site-serve',
            kwargs={'document_root': os.path.join(BASE_DIR, 'site'),
                    'show_indexes': True}),
]

# Serve the favicon - Keep for later
urlpatterns += [
    path('favicon.ico', serve, {
            'path': 'favicon.ico',
            'document_root': os.path.join(BASE_DIR, 'home/static'),
        }
    ),
]

# Switch to social login if it is configured - Keep for later
try:
    from . import github_settings
    social_login = 'registration/login_social.html'
    urlpatterns.insert(0,
                       path('accounts/login/', auth_views.LoginView.as_view(template_name=social_login))
                       )
    print('Using', social_login, 'as the login template')
except:
    print('Using AdPulse/templates/registration/login.html as the login template')

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
