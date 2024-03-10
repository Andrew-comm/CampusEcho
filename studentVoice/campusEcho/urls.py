
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('student/', views.studenthome, name='studenthome'),
    path('staff/', views.staffhome, name='staffhome'),
    path('signup/', views.signup_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
   
    path( 'staff_signin/', views.staff_login_view,name='staff-signin'),
    path( 'staff_signout/', views.staff_logout_view,name='staff-signout'),


    path('profile/', views.profile_view, name='profile'),
    path('profile/create/', views.profile_create_view, name='profile_create'),
    path('profile/update/', views.profile_update_view, name='profile_update'),

    path('create/', views.create_feedback, name='create_feedback'),
    path('list/', views.feedback_list, name='feedback_list'),
    path('<int:feedback_id>/', views.feedback_details, name='feedback_details'),
    path('all/', views.all_user_feedbacks, name='all_user_feedbacks'),
   
]