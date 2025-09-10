from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm
from .models import User

class UserRegisterView(CreateView):
    """
    Class-based view for user registration
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Account created successfully! Welcome to DrugTrack, {form.cleaned_data["first_name"]}!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register - DrugTrack'
        return context

class CustomLoginView(LoginView):
    """
    Custom login view with role-based redirect
    """
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirect to role-based dashboard
        user = self.request.user
        if user.is_authenticated:
            return user.get_dashboard_url()
        return reverse_lazy('dashboard:overview')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login - DrugTrack'
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Welcome back, {form.get_user().first_name}! You are logged in as {form.get_user().get_role_display()}.'
        )
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """
    Custom logout view
    """
    next_page = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)

@login_required
def profile_view(request):
    """
    User profile view with update functionality
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'title': 'Profile - DrugTrack',
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)

# Function-based view alternative for registration (if preferred)
def register_view(request):
    """
    Function-based registration view (alternative to class-based)
    """
    if request.user.is_authenticated:
        return redirect('dashboard:overview')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, 
                f'Account created successfully! Welcome to DrugTrack, {user.first_name}!'
            )
            return redirect(user.get_dashboard_url())
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Register - DrugTrack'
    }
    return render(request, 'users/register.html', context)