from django.urls import path
from . import views, api

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('memberdetails/<str:medicaid_id>/', views.memberdetails, name='memberdetails'),
    path('add_action/', views.add_action, name='add_action'),
    path('appointment_add_action/', views.appointment_add_action, name='appointment_add_action'),
    path('member_add_update_alert/', views.member_add_update_alert, name='member_add_update_alert'),
    path('add_member_alt_address/', views.add_member_alt_address, name='add_member_alt_address'),
    path('add_member_alt_pnone/', views.add_member_alt_pnone, name='add_member_alt_pnone'),
    path('add_member_alt_language/', views.add_member_alt_language, name='add_member_alt_language'),
    path('add_prisim_claim/', views.add_prisim_claim, name='add_prisim_claim'),
    path('add_rx_claim/', views.add_rx_claim, name='add_rx_claim'),
    # path('score_history/<int:employee_id>/<int:region_id>/', views.score_history, name='score_history'),
    # path('fscbyregion/<int:region_id>/', views.fscbyregion, name='fscbyregion'),
    path('update_member_indicator/', views.update_member_indicator, name='update_member_indicator'),
    path('update_member_info/', views.update_member_info, name='update_member_info'),
    path('starperformance/', views.star_performance, name='starperformance'),
    path('history/<str:medicaid_id>', views.memberhistory, name='history'),
    # path('contact_us/', views.contact_us, name='contact_us'),
    # path('admin_login/', views.admin_login, name='admin_login'),
    # path('leaderboard/', views.leaderboard, name='leaderboard'),
    # path('admin_score_history/<int:employee_id>/', views.admin_score_history, name='admin_score_history'),
    # path('admin_score_history/', views.admin_score_history, name='admin_score_history'),
    # path('thank_you/', views.thank_you, name='thank_you'),
     path('mywork/', views.mywork, name='mywork'),
    # path('region_manager_score/', views.region_manager_score, name='region_manager_score'),
    path('processmember/', views.processmember, name='processmember'),
    path('processriskgap/', views.processriskgap, name='processriskgap'),
    path('processquality/', views.processquality, name='processquality'),
    # client api list
    path("api/get_scheduled_action_status/", api.get_scheduled_action_status, name="get_scheduled_action_status"),
    path("api/get_vendor_list/", api.get_vendor_list, name="get_vendor_list"),
    path("api/get_doctor_list/", api.get_doctor_list, name="get_doctor_list"),
    path("api/get_alert_typeList/", api.get_alert_typeList, name="get_alert_typeList"),
    path('api/get_call_history/', api.get_call_history, name='get_call_history'),
    path('api/get_gap_list/', api.get_gap_list, name='get_gap_list')

]
