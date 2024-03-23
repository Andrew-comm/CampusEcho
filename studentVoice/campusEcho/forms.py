from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile , Feedback, Post, Comment

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='Email')  # Add an email field to the form

    class Meta(UserCreationForm.Meta):
        model = User  # Change 'User' to 'CustomUser'
        fields = UserCreationForm.Meta.fields + ('email', 'user_type',)  # Include 'email' and 'user_type' fields in the form

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']




class FeedbackForm(forms.ModelForm):
   
    class Meta:
        model = Feedback
        fields = ['category', 'severity', 'feedback_type', 'title', 'description', 'evidence', 'status']



class FeedbackSolutionForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['solution']




class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['content']
