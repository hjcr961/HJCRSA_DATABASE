from django.urls import path
from . import views
from .views import ActivityLogView
from django.contrib.auth import views as auth_views
from .views import login_view
from .views import login_view, home_view

urlpatterns = [
    
    # Add forms
    path('member/add/', views.add_main_member, name='add_main_member'),
    path('dependent/add/', views.add_dependent, name='add_dependent'),
    path('treasury/add/', views.add_treasury, name='add_treasury'),
    path('treasury-dep/add/', views.add_treasury_dep, name='add_treasury_dep'),
    
    # List views
    path('members/', views.member_list, name='member_list'),
    path('dependents/', views.dependent_list, name='dependent_list'),
    path('treasury/', views.treasury_list, name='treasury_list'),
    path('treasury-dep/', views.treasury_dep_list, name='treasury_dep_list'),
    path('activity-log/', ActivityLogView.as_view(), name='activity_log'),
    path('member/<int:pk>/edit/', views.MemberUpdateView.as_view(), name='edit_member'),
    path('api/member/<int:card_number>/payments/', views.member_payments, name='member_payments'),
    path('api/member/<int:card_number>/dependents/', views.member_dependents, name='member_dependents'),
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', views.home_view, name='home'),
    path('validate-card-number/', views.validate_card_number, name='validate_card_number'),
    path('api/member/<str:branch_member_number>/upload-picture/', views.upload_member_picture, name='upload_member_picture'),
    path('validate-card-number-add/', views.validate_card_number_add, name='validate_card_number_add'),
    path('api/dependent/<int:dependent_id>/payments/', views.dependent_payments, name='dependent_payments'),
    path('api/dependent/<int:dependent_id>/payments/', views.dependent_payments, name='dependent_payments'),
    path('signup/', views.signup_view, name='signup'),
    path('api/gender-distribution/', views.get_gender_distribution, name='gender_distribution'),
    path('upload-picture/', views.upload_picture, name='upload_picture'),





    
]
