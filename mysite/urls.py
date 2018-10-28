"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from auctionsapp import views
from mysite import settings

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')), #new
    path('admin/', admin.site.urls),
    path('auctionsapp/v1/', include('auctionsapp.urls')), #new
    path('auctionsapp-auth', include('rest_framework.urls')), #restframework  
]

urlpatterns += i18n_patterns(
    path('auctionsapp/v1/', include('auctionsapp.urls')), #new
    path('auctionsapp-auth', include('rest_framework.urls')), #restframework
    path(_('about/'), views.about, name='about'),
    prefix_default_language=False,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [ 
       url(r'^__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns

