from django.urls import include, path

from api import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('urlToVideoContent', views.url_to_video_content, name="url_to_video_content"),
    path('ping/', views.test, name="test"),
]
