from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, ProfileForm, FeedbackForm
from .models import Profile, Feedback, User
from django.contrib.auth.decorators import login_required

User = get_user_model()



def home(request):
    return render(request, 'home.html')


def studenthome(request):
    return render(request, 'student.html')

def staffhome(request):
    return render(request, 'staff_home.html')

def signup_view(request):
    error_message = None
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if get_user_model().objects.filter(email=email).exists():
                error_message = 'Email already exists!'
            else:
                user = form.save()
                if user.user_type == 'student':
                    return redirect('login')  # Redirect student users to the login page
                elif user.user_type == 'administrator':
                    return redirect('staff-signin')  # Redirect staff users to the staff login page
    return render(request, 'signup.html', {'form': form, 'error_message': error_message})

def login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.user_type == 'administrator':
                return redirect('staffhome')  # Redirect staff users to staff home page
            else:
                return redirect('studenthome')  # Redirect student users to home page
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')



def staff_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Assuming email is used for authentication
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None and user.user_type == 'administrator':
                login(request, user)
                return redirect('staffhome')  # Redirect staff users to staff home page
    else:
        form = AuthenticationForm()
    return render(request, 'staff_login.html', {'form': form})


def staff_logout_view(request):
    logout(request)
    return redirect('stafflogin')



@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('profile_create')
    return render(request, 'profile.html', {'profile': profile})

@login_required
def profile_create_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile')
    else:
        form = ProfileForm()
    return render(request, 'profile_create.html', {'form': form})


@login_required
def profile_create_view(request):
    try:
        profile = request.user.profile
        return redirect('profile')  # Redirect to profile view if profile already exists
    except Profile.DoesNotExist:
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return redirect('profile')
        else:
            form = ProfileForm()
        return render(request, 'profile_create.html', {'form': form})


@login_required
def profile_update_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('profile_create')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_update.html', {'form': form, 'profile': profile})  # Pass profile to the template


@login_required
def create_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('feedback_list')
    else:
        form = FeedbackForm()
    return render(request, 'create_feedback.html', {'form': form})

@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'feedback_list.html', {'feedbacks': feedbacks})

@login_required
def feedback_details(request, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id)
    return render(request, 'feedback_details.html', {'feedback': feedback})

@login_required
def all_user_feedbacks(request):
    if request.user.user_type == 'administrator':
        user_feedbacks = {}
        users = User.objects.all()
        for user in users:
            feedbacks = Feedback.objects.filter(submitted_by=user)
            user_feedbacks[user.username] = feedbacks
        return render(request, 'all_user_feedbacks.html', {'user_feedbacks': user_feedbacks})
    else:
        return redirect('feedback_list')
