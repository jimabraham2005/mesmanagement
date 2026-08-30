from django.db import models

# Create your models here.
from django import forms


class homemenu(models.Model):

    name = models.CharField(max_length=100)
    img= models.ImageField(upload_to ='pics') 
    des = models.TextField()
    price = models.IntegerField()
    offer = models.BooleanField(default=False)


messtime_choices = (
    ('Lunch', 'lunch'),
    ('Dinner', 'dinner')
)


    

class Hostel(models.Model):
    Hostel_Name = models.CharField(max_length= 30)
    Location = models.CharField(max_length= 30)
    def __str__(self):
        return self.Hostel_Name

    

class Menu(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )

    MEAL_CHOICES = (
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    )

    day = models.CharField(max_length=20, choices=DAY_CHOICES,null=True, blank=True)
    meal = models.CharField(max_length=20, choices=MEAL_CHOICES,null=True, blank=True)
    items = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.day} - {self.meal}"
    

from django.db import models
from django.contrib.auth.models import User


class Inventory(models.Model):

    item_name = models.CharField(max_length=100)

    quantity = models.FloatField(help_text="Quantity available")

    unit = models.CharField(
        max_length=20,
        choices=(
            ('kg', 'Kilogram'),
            ('litre', 'Litre'),
            ('packet', 'Packet'),
            ('piece', 'Piece'),
        )
    )

    last_updated = models.DateTimeField(auto_now=True)

    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['item_name']

    def __str__(self):
        return f"{self.item_name} - {self.quantity} {self.unit}"




class MessCut(models.Model):
    MEAL_CHOICES = (
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    meal = models.CharField(max_length=20, choices=MEAL_CHOICES)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.meal}"




class Attendance(models.Model):
    MEAL_CHOICES = (
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    meal = models.CharField(max_length=20, choices=MEAL_CHOICES)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date', 'meal')

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.meal}"



from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
        ('warden', 'Warden'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Student-specific details
    reg_no = models.CharField(max_length=20, blank=True, null=True)
    room_no = models.CharField(max_length=10, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username


# models.py
class Complaint(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)   # 👈 NEW
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.status}"


class Bill(models.Model):
    STATUS_CHOICES = (
        ('Unpaid', 'Unpaid'),
        ('Pending Approval', 'Pending Approval'),
        ('Paid', 'Paid'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_meals = models.IntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.start_date.strftime('%B %Y')}"
    
    class Meta:
        unique_together = ('student', 'start_date', 'end_date')

    

class WardenNotice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Notification(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.student.username}"
