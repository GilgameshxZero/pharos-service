from django.conf.urls import include, url
from .views import PrintView

urlpatterns = [
    url(r'^66d2b8f4a09cd35cb23076a1da5d51529136a3373fd570b122/?$', PrintView.as_view()) 
]
