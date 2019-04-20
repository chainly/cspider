from django.conf.urls import url
from t import views


urlpatterns = [
    url(r'^$', views.xterm),
]

