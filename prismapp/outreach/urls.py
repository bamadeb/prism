from django.urls import path
from . import views, api

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('memberdetails/<int:medicaid_id>/', views.memberdetails, name='memberdetails'),
    path('add_action/', views.add_action, name='add_action'),
    path('appointment_add_action/', views.appointment_add_action, name='appointment_add_action'),
    path('history/<int:medicaid_id>', views.memberhistory, name='history'),
    # path('manager_score/', views.manager_score, name='manager_score'),
    # path('register/', views.register, name='register'),
    # path('point_by_region/', views.point_by_region, name='point_by_region'),
    # path('your_current_rank/', views.your_current_rank, name='your_current_rank'),
    # path('prize/', views.prize, name='prize'),
    # path('score_history/', views.score_history, name='score_history'),
    # path('score_history/<int:employee_id>/<int:region_id>/', views.score_history, name='score_history'),
    # path('fscbyregion/<int:region_id>/', views.fscbyregion, name='fscbyregion'),
    # path('fscbyregion/', views.fscbyregion, name='fscbyregion'),
    # path('care_credit/', views.care_credit, name='care_credit'),
    # path('contact_us/', views.contact_us, name='contact_us'),
    # path('admin_login/', views.admin_login, name='admin_login'),
    # path('leaderboard/', views.leaderboard, name='leaderboard'),
    # path('admin_score_history/<int:employee_id>/', views.admin_score_history, name='admin_score_history'),
    # path('admin_score_history/', views.admin_score_history, name='admin_score_history'),
    # path('thank_you/', views.thank_you, name='thank_you'),
     path('mywork/', views.mywork, name='mywork'),
    # path('region_manager_score/', views.region_manager_score, name='region_manager_score'),

    # client api list
    path("api/get_scheduled_action_status/", api.get_scheduled_action_status, name="get_scheduled_action_status"),
    path("api/get_vendor_list/", api.get_vendor_list, name="get_vendor_list"),
    path("api/get_doctor_list/", api.get_doctor_list, name="get_doctor_list"),
    # APIs URL
    path('api/get_call_history/', api.get_call_history, name='get_call_history')

]
