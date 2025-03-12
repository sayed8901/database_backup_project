from django.contrib import admin
from django.urls import path

from scheduler import scheduler



urlpatterns = [
    path('admin/', admin.site.urls),
]


# to auto start the scheduler
scheduler.start()
