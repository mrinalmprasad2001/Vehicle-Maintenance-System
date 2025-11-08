from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('servicer_dashboard/', views.servicer_dashboard, name='servicer_dashboard'),
    path('assign_servicer/<int:service_id>/', views.assign_servicer, name='assign_servicer'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_vehicle/', views.add_vehicle, name='add_vehicle'),
    path('book_service/', views.book_service, name='book_service'),
    path('update_service/<int:service_id>/', views.update_service_status, name='update_service_status'),
    path('feedback/<int:service_id>/', views.submit_feedback, name='submit_feedback'),
]