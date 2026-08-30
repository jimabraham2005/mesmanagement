

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from . models import *
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Count
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from calendar import monthrange
import calendar
from django.http import HttpResponse

import openpyxl
# Create your views here.

def user_logout(request):
    auth.logout(request)
    return redirect('/')



# accounts/views.py


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Role is forced to 'student' for public registration
        role = 'student'

        reg_no = request.POST.get('reg_no')
        room_no = request.POST.get('room_no')
        department = request.POST.get('department')
        phone = request.POST.get('phone')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)

        Profile.objects.create(
            user=user,
            role=role,
            reg_no=reg_no,
            room_no=room_no,
            department=department,
            phone=phone
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'Signup.html')


from django.contrib.auth import authenticate, login

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            role = user.profile.role

            if role == 'admin':
                return redirect('admin_dashboard')
            elif role == 'warden':
                return redirect('warden_dashboard')
            else:
                return redirect('studentdashboard')

        messages.error(request, "Invalid login credentials")

    return render(request, 'login.html')
  


                       
        


def index(request):

    dests = homemenu.objects.all()    
    return render(request, 'index.html', {'dests': dests}) 

def menu(request):
    Lmenu = Menu.objects.filter(time='Lunch')
    Dmenu = Menu.objects.filter(time='Dinner')
    return render(request,'menu.html',context={'Lmenu':Lmenu,'Dmenu':Dmenu})



def result(request):
    
    return render(request, 'result.html') 


def empregister(request):
    
    return render(request, 'employee_register.html') 





#admin 


@login_required
def admindashboard(request):
    if request.user.profile.role != 'admin':
        return redirect('login')
        
    today = now().date()

    # Total students (role-based)
    total_students = Profile.objects.filter(role='student').count()

    # Today's attendance (unique students)
    today_attendance = Attendance.objects.filter(
        date=today
    ).values('student').distinct().count()
    complaints = Complaint.objects.all().count()
    
    # Billing summary
    pending_payments = Bill.objects.filter(paid=False).count()

    context = {
        'total_students': total_students,
        'today_attendance': today_attendance,
        'complaints': complaints,
        'pending_payments': pending_payments,
    }

    return render(request, 'admin/admindashboard.html', context)



@login_required
def adminMenuManagement(request):
    if request.user.profile.role != 'admin':
        return redirect('login')
        
    if request.method == 'POST':
        day = request.POST.get('day')
        meal = request.POST.get('meal')
        items = request.POST.get('items')

        # Check for duplicate menu
        if Menu.objects.filter(day=day, meal=meal).exists():
            messages.error(request, f"A menu for {day} - {meal} already exists!")
        else:
            Menu.objects.create(day=day, meal=meal, items=items)
            messages.success(request, "Menu added successfully!")

        return redirect('menumanagement')

    menus = Menu.objects.all().order_by('day', 'meal')
    return render(request, 'admin/MenuManagement.html', {'menus': menus})


# Edit Menu
@login_required
def edit_menu(request, menu_id):
    if request.user.profile.role != 'admin':
        return redirect('login')
        
    menu = get_object_or_404(Menu, id=menu_id)

    # Pass days and meals as lists
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meals = ["Breakfast", "Lunch", "Dinner"]

    if request.method == 'POST':
        menu.day = request.POST.get('day')
        menu.meal = request.POST.get('meal')
        menu.items = request.POST.get('items')
        menu.save()
        return redirect('menumanagement')

    return render(request, 'admin/EditMenu.html', {
        'menu': menu,
        'days': days,
        'meals': meals
    })

# Delete Menu
@login_required
def delete_menu(request, menu_id):
    if request.user.profile.role != 'admin':
        return redirect('login')
    menu = get_object_or_404(Menu, id=menu_id)
    menu.delete()
    return redirect('menumanagement')

@login_required
def adminattendance(request):
    if request.user.profile.role != 'admin':
        return redirect('login')
        
    today = now().date()

    attendances = Attendance.objects.filter(
        date=today
    ).select_related('student', 'student__profile')

    attendance_map = defaultdict(set)

    for att in attendances:
        attendance_map[att.student].add(att.meal)

    context = {
        'attendance_map': dict(attendance_map),
        'today': today
    }


    return render(request, 'admin/adminAttendance.html', context)

@login_required
def admin_mess_cut_list(request):
    if request.user.profile.role != 'admin':
        return redirect('login')
    mess_cuts = MessCut.objects.all().order_by('-date')

    return render(request, 'admin/MessRequest.html', {
        'mess_cuts': mess_cuts
    })


def update_mess_cut_status(request, cut_id, action):
    mess_cut = get_object_or_404(MessCut, id=cut_id)

    if action == 'approve':
        mess_cut.status = 'Approved'
        Notification.objects.create(
            student=mess_cut.student,
            message=f"Your mess cut request for {mess_cut.date} ({mess_cut.meal}) has been Approved."
        )
        messages.success(request, "Mess cut approved successfully.")

    elif action == 'reject':
        mess_cut.status = 'Rejected'
        Notification.objects.create(
            student=mess_cut.student,
            message=f"Your mess cut request for {mess_cut.date} ({mess_cut.meal}) has been Rejected."
        )
        messages.warning(request, "Mess cut rejected.")

    mess_cut.save()
    return redirect('admin_mess_cut_list')


@login_required
def admin_student_list(request):
    students = Profile.objects.filter(role='student').select_related('user')

    context = {
        'students': students
    }
    return render(request, 'admin/adminStudent.html', context)


@login_required
def admin_complaints(request):
    if request.user.profile.role != 'admin':
        return redirect('login')

    if request.method == "POST":
        complaint_id = request.POST.get('complaint_id')
        action = request.POST.get('action')
        reply = request.POST.get('admin_reply')

        complaint = Complaint.objects.get(id=complaint_id)

        complaint.admin_reply = reply

        if action == "resolve":
            complaint.status = "Resolved"
            complaint.resolved_at = now()
            Notification.objects.create(
                student=complaint.student,
                message=f"Your complaint '{complaint.subject}' has been Resolved. Reply: {reply}"
            )

        elif action == "reject":
            complaint.status = "Rejected"
            complaint.resolved_at = now()
            Notification.objects.create(
                student=complaint.student,
                message=f"Your complaint '{complaint.subject}' has been Rejected. Reply: {reply}"
            )

        complaint.save()
        return redirect('admin_complaints')

    complaints = Complaint.objects.all().order_by('-created_at')

    return render(request, 'admin/adminComplaint.html', {
        'complaints': complaints
    })

MEAL_COST=50

@login_required
def admin_generate_bill(request):
    if request.user.profile.role != 'admin':
        return redirect('login')
        
    selected_month = request.GET.get('month')
    bills = Bill.objects.all().order_by('-start_date', 'student__username')

    # Handle Generation (POST)
    if request.method == 'POST' and 'generate' in request.POST:
        gen_month = request.POST.get('month')
        if gen_month:
            try:
                year, month = map(int, gen_month.split('-'))
                start_date = date(year, month, 1)
                end_date = date(year, month, calendar.monthrange(year, month)[1])

                students = User.objects.filter(profile__role='student')
                generated_count = 0

                for student in students:
                    total_meals = Attendance.objects.filter(
                        student=student,
                        date__range=(start_date, end_date)
                    ).count()

                    approved_cuts = MessCut.objects.filter(
                        student=student,
                        status='Approved',
                        date__range=(start_date, end_date)
                    ).count()

                    payable_meals = max(total_meals - approved_cuts, 0)

                    if payable_meals > 0:
                        amount = payable_meals * MEAL_COST
                        bill, created = Bill.objects.update_or_create(
                            student=student,
                            start_date=start_date,
                            end_date=end_date,
                            defaults={
                                'total_meals': payable_meals,
                                'amount': amount
                            }
                        )
                        if created:
                            Notification.objects.create(
                                student=student,
                                message=f"A new bill of ₹{amount} has been generated for {start_date.strftime('%B %Y')}."
                            )
                        generated_count += 1
                
                return redirect(f"{request.path}?month={gen_month}")
            except ValueError:
                messages.error(request, "Invalid month format.")

    # Handle Filtering (GET)
    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            start_date = date(year, month, 1)
            bills = bills.filter(start_date=start_date)
        except ValueError:
            pass

    return render(request, 'admin/generateBill.html', {
        'bills': bills,
        'selected_month': selected_month
    })


@login_required
def admin_update_bill_status(request, bill_id, status):
    if request.user.profile.role != 'admin':
        return redirect('login')
    
    bill = get_object_or_404(Bill, id=bill_id)
    bill.status = status
    if status == 'Paid':
        bill.paid = True
    else:
        bill.paid = False
    bill.save()

    Notification.objects.create(
        student=bill.student,
        message=f"Your bill for {bill.start_date.strftime('%B %Y')} status has been updated to: {status}."
    )
    
    messages.success(request, f"Bill status updated to {status}")
    return redirect('admin_generate_bill')





@login_required
def export_students_excel(request):
    if request.user.profile.role != 'admin':
        return redirect('login')
    # Create workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Registered Students"

    # Header row
    headers = ['Register No',  'Username', 'Room No', 'Department', 'Phone', 'Role']
    ws.append(headers)

    # Get all students
    students = User.objects.filter(profile__role='student')

    for student in students:
        ws.append([
            student.profile.reg_no,
            student.username,
            student.profile.room_no,
            student.profile.department,
            student.profile.phone,
            student.profile.role,
        ])

    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=Registered_Students.xlsx'

    wb.save(response)
    return response

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Profile

from .models import Profile

@login_required
def add_warden(request):
    if request.user.profile.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('add_warden')

        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # ✅ CREATE PROFILE HERE
        Profile.objects.create(
            user=user,
            role='warden',
            phone=phone
        )

        messages.success(request, "Warden added successfully")
        return redirect('admin_dashboard')

    return render(request, 'admin/addWarden.html')


#student


@login_required
def studentdashboard(request):
    total_attendance = Attendance.objects.filter(student=request.user).count()
    mess_cuts_count = MessCut.objects.filter(student=request.user).count()
    pending_bills = Bill.objects.filter(student=request.user, paid=False)
    
    # Get unread notifications for badge
    unread_notifications_count = Notification.objects.filter(student=request.user, is_read=False).count()

    context = {
        'total_attendance': total_attendance,
        'mess_cuts_count': mess_cuts_count,
        'pending_bills': pending_bills,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request,'student/StudentDashboard.html', context)

from django.shortcuts import render
from .models import Menu
from datetime import datetime

@login_required
def student_daily_menu(request):
    if request.user.profile.role != 'student':
        return redirect('login')
    today_day = datetime.today().strftime('%A')  # e.g., 'Monday'
    today_menus = Menu.objects.filter(day=today_day).order_by('meal')

    # Prepare items list for template
    for menu in today_menus:
        menu.items_list = [item.strip() for item in menu.items.split(',')]

    context = {
        'today_menus': today_menus,
        'today_day': today_day,
    }
    return render(request, 'student/studentmenu.html', context)


@login_required
def student_weekly_menu(request):
    if request.user.profile.role != 'student':
        return redirect('login')
    menus = Menu.objects.all().order_by('day', 'meal')

    # Prepare items list for template
    for menu in menus:
        menu.items_list = [item.strip() for item in menu.items.split(',')]

    context = {
        'menus': menus
    }
    return render(request, 'student/WeeklyMenu.html', context)


@login_required
def student_apply_mess_cut(request):
    if request.user.profile.role != 'student':
        return redirect('login')
    if request.method == 'POST':
        date = request.POST.get('date')
        meal = request.POST.get('meal')
        reason = request.POST.get('reason')

        # Prevent duplicate mess cut
        if MessCut.objects.filter(student=request.user, date=date, meal=meal).exists():
            messages.error(request, "Mess cut already applied for this date and meal.")
        else:
            MessCut.objects.create(
                student=request.user,
                date=date,
                meal=meal,
                reason=reason
            )
            messages.success(request, "Mess cut applied successfully.")

        return redirect('student_mess_cut')

    mess_cuts = MessCut.objects.filter(student=request.user).order_by('-date')

    return render(request, 'student/MessCut.html', {
        'mess_cuts': mess_cuts
    })




@login_required
def student_attendance(request):
    if request.user.profile.role != 'student':
        return redirect('login')
    meals = ['Breakfast', 'Lunch', 'Dinner']

    # Example: already marked meals for today
    marked_meals = Attendance.objects.filter(
        student=request.user,
        date=date.today()
    ).values_list('meal', flat=True)

    if request.method == 'POST':
        meal = request.POST.get('meal')

        if meal not in marked_meals:
            Attendance.objects.create(
                student=request.user,
                meal=meal,
                date=date.today()
            )
            messages.success(request, f"{meal} attendance marked")

        return redirect('student_attendance')

    return render(request, 'student/StudentAttendance.html', {
        'meals': meals,
        'marked_meals': marked_meals
    })




@login_required
def student_complaint(request):
    if request.user.profile.role != 'student':
        return redirect('login')
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        Complaint.objects.create(
            student=request.user,
            subject=subject,
            message=message
        )

        messages.success(request, "Complaint submitted successfully!")
        return redirect('studentdashboard')

    return render(request, 'student/studentComplaint.html')


@login_required
def admin_resolve_complaint(request, complaint_id):
    if request.user.profile.role != 'admin':
        return redirect('login')
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.status = 'Resolved'
    complaint.save()
    messages.success(request, "Complaint marked as resolved.")
    return redirect('admin_complaints')


@login_required
def delete_complaint(request, complaint_id):
    if request.user.profile.role not in ['admin', 'warden']:
        return redirect('login')
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.delete()
    messages.warning(request, "Complaint deleted.")
    if request.user.profile.role == 'admin':
        return redirect('admin_complaints')
    return redirect('warden_complaints')


@login_required
def student_complaint_status(request):
    if request.user.profile.role != 'student':
        return redirect('login')
    complaints = Complaint.objects.filter(
        student=request.user
    ).order_by('-created_at')

    return render(request, 'student/complaintTracking.html', {
        'complaints': complaints
    })



#warden

@login_required
def warden_dashboard(request):
    if request.user.profile.role != 'warden':
        return redirect('login')
    pending_complaints = Complaint.objects.filter(status='Pending').count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    total_notices = WardenNotice.objects.count()

    return render(request, 'warden/dashboard.html', {
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'total_notices': total_notices
    })


@login_required
def warden_profile(request):
    if request.user.profile.role != 'warden':
        return redirect('login')
    
    profile = request.user.profile
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        request.user.email = email
        request.user.save()
        
        profile.phone = phone
        profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('warden_profile')

    return render(request, 'warden/profile.html', {'profile': profile})





@login_required
def warden_complaints(request):
    if request.user.profile.role != 'warden':
        return redirect('login')
    complaints = Complaint.objects.all().order_by('-created_at')

    return render(request, 'warden/complaints.html', {
        'complaints': complaints
    })



@login_required
def warden_resolve_complaint(request, complaint_id):
    if request.user.profile.role != 'warden':
        return redirect('login')
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        reply = request.POST.get('reply')
        complaint.admin_reply = reply # Standardizing on admin_reply field
        complaint.status = 'Resolved'
        complaint.resolved_at = now()
        complaint.save()
        
        Notification.objects.create(
            student=complaint.student,
            message=f"Your complaint '{complaint.subject}' has been Resolved by Warden. Reply: {reply}"
        )
        
        return redirect('warden_complaints')

    return render(request, 'warden/resolve_complaint.html', {
        'complaint': complaint
    })


@login_required
def add_notice(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')

        notice = WardenNotice.objects.create(
            title=title,
            message=message,
            created_by=request.user
        )
        
        # Notify all students
        students = User.objects.filter(profile__role='student')
        for student in students:
            Notification.objects.create(
                student=student,
                message=f"New Notice from Warden: {title}"
            )
            
        return redirect('warden_notices')

    return render(request, 'warden/add_notice.html')


@login_required
def warden_notices(request):
    if request.user.profile.role != 'warden':
        return redirect('login')
    notices = WardenNotice.objects.all().order_by('-created_at')
    return render(request, 'warden/notices.html', {
        'notices': notices
    })

@login_required
def student_notifications(request):
    notifications = Notification.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'student/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, student=request.user)
    notification.is_read = True
    notification.save()
    return redirect('student_notifications')

@login_required
def student_warden_notices(request):
    notices = WardenNotice.objects.all().order_by('-created_at')
    return render(request, 'student/warden_notices.html', {'notices': notices})


@login_required
def student_pay_bill(request, bill_id):
    if request.user.profile.role != 'student':
        return redirect('login')
    
    bill = get_object_or_404(Bill, id=bill_id, student=request.user)
    
    if request.method == 'POST':
        # Dummy payment logic
        bill.status = 'Pending Approval'
        bill.save()
        
        messages.success(request, "Payment submitted for approval. Admin will verify it soon.")
        return redirect('studentdashboard')
    
    return render(request, 'student/pay_bill.html', {'bill': bill})
