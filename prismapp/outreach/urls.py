from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('memberdetails/', views.memberdetails, name='memberdetails'),
    #path('resetpassword/<str:token>/', views.resetpassword, name='resetpassword'),
    # path('logoutadmin/', views.logoutadmin, name='logoutadmin'),
    # path('your_score/', views.your_score, name='your_score'),
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

]
