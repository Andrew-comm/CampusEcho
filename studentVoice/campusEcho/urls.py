
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



    path('community/', views.community_feed_list, name='community_feed'),
    path('create-post', views.community_feed_create, name='create-post'),
    path('comments/<int:post_id>/', views.add_comment, name='comments'), 
    path('likes/<int:post_id>/', views.like_post, name='like_post'),



    path('admin/feedback/', views.admin_feedback_list, name='admin_feedback_list'),
    path('resolve-feedback/<int:feedback_id>/', views.resolve_feedback, name='resolve_feedback'),

   
]