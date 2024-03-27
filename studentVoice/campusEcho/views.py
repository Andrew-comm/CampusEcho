from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
import dotenv

dotenv.load_dotenv()
import os

from .forms import CustomUserCreationForm, ProfileForm, FeedbackForm, FeedbackSolutionForm, PostForm, CommentForm

from .models import Profile, Feedback, User, Post , Comment, Like
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()


TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')





def home(request):
    return render(request, 'home.html')

def studenthome(request):
    # Assuming you have a way to identify the current student, for example, through authentication
    # Assuming the current user is the student

    # Filter feedbacks associated with the current student that are not resolved
    feedbacks = Feedback.objects.filter(student=request.user, status='pending').order_by('-submitted_at')

    # Filter resolved feedbacks associated with the current student
    resolved_feedbacks = Feedback.objects.filter(student=request.user, status='resolved').order_by('-submitted_at')

    context = {
        'feedbacks': feedbacks,
        'resolved_feedbacks': resolved_feedbacks,
    }
    return render(request, 'student.html', context)

def staffhome(request):
    user = request.user    
    feedbacks = Feedback.objects.all().order_by('-submitted_at')   
   
    # Iterate over feedbacks and get the profile associated with each student
   


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

    paginator = Paginator(feedbacks, 3)  #  feedbacks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'feedbacks': page_obj,
        # 'feedbacks': feedbacks,
        'category_choices': Feedback.CATEGORY_CHOICES,
        'severity_choices': Feedback.SEVERITY_CHOICES,
        'feedback_type_choices': Feedback.FEEDBACK_TYPE_CHOICES,
        'selected_category': category,
        'selected_severity': severity,
        'selected_feedback_type': feedback_type,
        'user': user,
       
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

            feedback.save()  # Save the model changes first 

            # Check if the feedback has an associated user and profile
            if feedback.student and feedback.student.profile and feedback.student.profile.phone_number:
                user_phone_number = feedback.student.profile.phone_number
                sms_body = f"We have resolved your feedback: {feedback.title}. Solution: {feedback.solution}"
                send_sms_notification(user_phone_number, sms_body)
                
                # Sending Email
                if feedback.student.email:
                    email_subject = "Feedback Resolution Notification"
                    email_body = render_to_string('feedback_resolution_email.html', {'feedback': feedback})
                    plain_email_body = strip_tags(email_body)
                    send_mail(email_subject, plain_email_body, 'ndrwrono2001@gmail.com', [feedback.student.email], html_message=email_body)

            else:
                print("Unable to send SMS and Email: student, profile, or phone number not found")

            
        return redirect('staffhome')
    else:
        return redirect('staffhome')

def send_sms_notification(phone_number, message):
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Send SMS message
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )

        print(f"SMS sent to {phone_number} with message: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")

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
            # Save the form but don't commit yet
            feedback = form.save(commit=False)
            # Associate the feedback with the current user
            feedback.student = request.user
            # Save the feedback with the user association
            feedback.save()
            return redirect('feedback_list')
    else:
        form = FeedbackForm()
    return render(request, 'create_feedback.html', {'form': form})

@login_required
def feedback_list(request):
    # Filter feedbacks to show only those associated with the current user
    feedbacks = Feedback.objects.filter(student=request.user)
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


#forum
def community_feed_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community_feed.html', {'posts': posts})

def community_feed_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('community_feed')  # Redirect to list view after success
    else:
        form = PostForm()
    return render(request, 'community_feed_create.html', {'form': form})

def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('community_feed')
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'post': post})


def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    # Check if the user has already liked the post
    if request.method == 'POST':
        user = request.user
        if Like.objects.filter(post=post, user=user).exists():
            # If the user has already liked the post, do nothing (can be used to unlike later)
            pass
        else:
            # If the user has not liked the post, create a new Like instance
            Like.objects.create(post=post, user=user)
    return redirect('community_feed')
