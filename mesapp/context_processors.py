from .models import Notification

def notification_context(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'student':
        unread_count = Notification.objects.filter(student=request.user, is_read=False).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}
