from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog
from django.utils.deprecation import MiddlewareMixin

class ActivityTrackingMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only log specific views to reduce overhead
        if request.user.is_authenticated:
            try:
                ActivityLog.objects.create(
                    user=request.user,
                    action='LOGIN' if request.path == '/login/' else 'ACCESS',
                    timestamp=timezone.now(),
                    description=f"Accessed {request.path}",
                    content_type=ContentType.objects.get_for_model(request.user),
                    object_id=request.user.id
                )
            except Exception:
                # Silently handle logging errors to prevent disrupting user experience
                pass
        return None

    def log_activity(self, request):
        action_map = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'DELETE': 'DELETE'
        }
        
        ActivityLog.objects.create(
            user=request.user,
            action=action_map.get(request.method),
            timestamp=timezone.now(),
            description=f"{request.method} request to {request.path}",
            content_type=ContentType.objects.get_for_model(request.user),
            object_id=request.user.id
        )
