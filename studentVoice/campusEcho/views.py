from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, ProfileForm, FeedbackForm, FeedbackSolutionForm

from .models import Profile, Feedback, User
from django.contrib.auth.decorators import login_required

User = get_user_model()



def home(request):
    return render(request, 'home.html')

def studenthome(request):
    # Assuming you have a way to identify the current student, for example, through authentication
    current_student = request.user  # Assuming the current user is the student

    # Filter feedbacks associated with the current student
    feedbacks = Feedback.objects.filter(student=current_student)

    # Filter resolved feedbacks associated with the current student
    resolved_feedbacks = Feedback.objects.filter(student=current_student, status='resolved')

    context = {
        'feedbacks': feedbacks,
        'resolved_feedbacks': resolved_feedbacks,
    }
    return render(request, 'student.html', context)

def staffhome(request):
    feedbacks = Feedback.objects.all()

    # Get filter parameters from the request
    category = request.GET.get('category')
    severity = request.GET.get('severity')
    feedback_type = request.GET.get('feedback_type')

    # Filter feedbacks based on provided parameters
    if category:
        feedbacks = feedbacks.filter(category=category)
    if severity:
        feedbacks = feedbacks.filter(severity=severity)
    if feedback_type:
        feedbacks = feedbacks.filter(feedback_type=feedback_type)

    context = {
        'feedbacks': feedbacks,
        'category_choices': Feedback.CATEGORY_CHOICES,
        'severity_choices': Feedback.SEVERITY_CHOICES,
        'feedback_type_choices': Feedback.FEEDBACK_TYPE_CHOICES,
        'selected_category': category,
        'selected_severity': severity,
        'selected_feedback_type': feedback_type,
    }
    return render(request, 'staff_home.html', context)

def resolve_feedback(request, feedback_id):
    if request.method == 'POST':
        feedback = Feedback.objects.get(id=feedback_id)
        recommendation = request.POST.get('recommendation')
        solution = request.POST.get('solution')
        if recommendation:
            feedback.recommendation = recommendation
        if solution:
            feedback.solution = solution
            feedback.status = 'resolved'
        feedback.save()
        return redirect('staffhome')
    else:
        return redirect('staffhome')
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
    return redirect('home')



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



@login_required
def admin_feedback_list(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'admin_feedback_list.html', {'feedbacks': feedbacks})
