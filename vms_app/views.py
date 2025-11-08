from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegisterForm, LoginForm, VehicleForm, ServiceRequestForm, FeedbackForm
from .models import UserProfile, Vehicle, ServiceRequest, Feedback

# Create your views here.

def home(request):
    return render(request,'home.html')

def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login_user')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')

                try:
                    profile = UserProfile.objects.get(user=user)
                except UserProfile.DoesNotExist:
                    messages.error(request, "User profile not found.")
                    return redirect('login')

                if profile.role == 'customer':
                    return redirect('customer_dashboard')
                elif profile.role == 'servicer':
                    return redirect('servicer_dashboard')
                elif profile.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Invalid user role.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

@login_required
def customer_dashboard(request):
    vehicles = Vehicle.objects.filter(owner=request.user)
    services = ServiceRequest.objects.filter(customer=request.user)
    return render(request, 'customer_dashboard.html', {'vehicles': vehicles, 'services': services})

@login_required
def servicer_dashboard(request):
    services = ServiceRequest.objects.filter(servicer=request.user)
    return render(request, 'servicer_dashboard.html', {'services': services})

def assign_servicer(request, service_id):
    if request.method == 'POST':
        servicer_id = request.POST.get('servicer_id')
        service = get_object_or_404(ServiceRequest, id=service_id)
        servicer = get_object_or_404(User, id=servicer_id)
        service.servicer = servicer
        service.save()
        messages.success(request, f"Servicer {servicer.username} assigned successfully!")
    return redirect('admin_dashboard')

@login_required
def admin_dashboard(request):
    users = UserProfile.objects.all()
    services = ServiceRequest.objects.all()
    feedbacks = Feedback.objects.all()
    servicers = User.objects.filter(userprofile__role='servicer')  # Only fetch users with servicer role
    return render(request, 'admin_dashboard.html', {
        'users': users,
        'services': services,
        'feedbacks': feedbacks,
        'servicers': servicers
    })

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            messages.success(request, "Vehicle added successfully!")
            return redirect('customer_dashboard')
    else:
        form = VehicleForm()
    return render(request, 'add_vehicle.html', {'form': form})

@login_required
def book_service(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        form.fields['vehicle'].queryset = Vehicle.objects.filter(owner=request.user)  # Filter vehicles
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.customer = request.user
            service_request.save()
            return redirect('customer_dashboard')
    else:
        form = ServiceRequestForm()
        form.fields['vehicle'].queryset = Vehicle.objects.filter(owner=request.user)  # Filter vehicles
    return render(request, 'book_service.html', {'form': form})

@login_required
def update_service_status(request, service_id):
    service = get_object_or_404(ServiceRequest, id=service_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        service.status = new_status
        service.save()
        subject = f"Service Update for Vehicle {service.vehicle.vehicle_number}"
        message = (
            f"Dear {service.customer.username},\n\n"
            f"The status of your vehicle service (Vehicle No: {service.vehicle.vehicle_number}) "
            f"has been updated to: {new_status}.\n\n"
            f"Service Details:\n"
            f"- Vehicle Model: {service.vehicle.vehicle_model}\n"
            f"- Description: {service.description}\n"
            f"- Service Date: {service.service_date}\n\n"
            f"Thank you for choosing our Revitrax Maintenance Services!\n\n"
            f"Best regards,\n"
            f"Revitrax Team"
        )
        recipient = service.customer.email
        if recipient:
            send_mail(subject, message, None, [recipient], fail_silently=False)
        messages.success(request, f"Service status updated to {new_status} and email sent to customer.")
        return redirect('servicer_dashboard')
    return redirect('servicer_dashboard')

@login_required
def submit_feedback(request, service_id):
    service = get_object_or_404(ServiceRequest, id=service_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.customer = request.user
            feedback.service_request = service
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('customer_dashboard')
    else:
        form = FeedbackForm()
    return render(request, 'feedback_form.html', {'form': form})