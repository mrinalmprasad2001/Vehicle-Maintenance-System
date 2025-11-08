from django.contrib import admin
from .models import UserProfile, Vehicle, ServiceRequest, Feedback

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Vehicle)
admin.site.register(ServiceRequest)
admin.site.register(Feedback)