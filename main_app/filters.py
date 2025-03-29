import django_filters
from .models import ActivityLog

class ActivityLogFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='timestamp', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='timestamp', lookup_expr='lte')
    action = django_filters.ChoiceFilter(choices=ActivityLog.ACTIONS)
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')

    class Meta:
        model = ActivityLog
        fields = ['date_from', 'date_to', 'action', 'user']
