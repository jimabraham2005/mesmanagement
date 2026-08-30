"""
URL configuration for mesmanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('about/',views.about, name='about'), 
    path('student_register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),



    #admin

    path('admindashboard',views.admindashboard,name='admin_dashboard'),
    path('menumanagement',views.adminMenuManagement,name='menumanagement'),
    path('edit-menu/<int:menu_id>/', views.edit_menu, name='edit_menu'),
    path('delete-menu/<int:menu_id>/', views.delete_menu, name='delete_menu'),
    path('adminattendance', views.adminattendance, name='attendance'),
    # path('inventory/', views.inventory_page, name='inventory'),
    path('mess-cuts/', views.admin_mess_cut_list, name='admin_mess_cut_list'),
    path('mess-cut/<int:cut_id>/<str:action>/', views.update_mess_cut_status, name='update_mess_cut_status'),
    path('students/', views.admin_student_list, name='admin_students'),
    path('complaints/', views.admin_complaints, name='admin_complaints'),
    path('complaint/resolve/<int:complaint_id>/',views.admin_resolve_complaint, name='admin_resolve_complaint'),
    path('complaint/delete/<int:complaint_id>/', views.delete_complaint, name='delete_complaint'),
    path('generatebill/',views.admin_generate_bill,name='admin_generate_bill'),
    path('bill/update-status/<int:bill_id>/<str:status>/', views.admin_update_bill_status, name='admin_update_bill_status'),
    path('export-students/', views.export_students_excel, name='export_students_excel'),
    path('add-warden/', views.add_warden, name='add_warden'),





    #student

    path('studentdashboard',views.studentdashboard,name='studentdashboard'),
    path('studentmenu',views.student_daily_menu,name='studentmenu'),
    path('student/weekly-menu/', views.student_weekly_menu, name='student_weekly_menu'),
    path('student/mess-cut/', views.student_apply_mess_cut, name='student_mess_cut'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/complaint/', views.student_complaint, name='student_complaint'),
    
    path('student/complaints/', views.student_complaint_status, name='student_complaint_status'),
    path('student/notifications/', views.student_notifications, name='student_notifications'),
    path('student/notification/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('student/warden-notices/', views.student_warden_notices, name='student_warden_notices'),
    path('student/pay-bill/<int:bill_id>/', views.student_pay_bill, name='student_pay_bill'),



    #warden

    path('warden/dashboard/', views.warden_dashboard, name='warden_dashboard'),
    path('warden/profile/', views.warden_profile, name='warden_profile'),
    path('warden/complaints/', views.warden_complaints, name='warden_complaints'),
    path('warden/complaint/<int:complaint_id>/resolve/', views.warden_resolve_complaint, name='warden_resolve_complaint'),
    path('warden/notices/', views.warden_notices, name='warden_notices'),
    path('warden/notices/add/', views.add_notice, name='add_notice'),






    


]
