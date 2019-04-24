"""messpbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic.base import RedirectView
from django.http import HttpResponse

# Create your views here


def default_get(request):
    print(request.GET)
    return HttpResponse('Welcome to pharos-service! You probably want to head to /messprint/66d2b8f4a09cd35cb23076a1da5d51529136a3373fd570b122<br><br>Made by Yang Yan, Stella Yang, Tony Wang, and Jing Lin')


urlpatterns = [
    url(r'^$', default_get),
    url(r'^admin/', admin.site.urls),
    url(r'^messprint/', include('messprint.urls')),
]

