from django_filters import rest_framework as filters
from .models import Circle
from django.db.models import Count

class CircleFilter(filters.FilterSet):
    """サークル検索用のフィルター"""
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=Circle.CIRCLE_STATUS_CHOICES)
    circle_type = filters.ChoiceFilter(choices=Circle.CIRCLE_TYPE_CHOICES)
    interests = filters.ModelMultipleChoiceFilter(
        field_name='interests__id',
        to_field_name='id',
        queryset=lambda request: request.interests.all()
    )
    member_count = filters.RangeFilter(
        field_name='memberships',
        method='filter_member_count'
    )
    created_at = filters.DateTimeFromToRangeFilter()
    last_activity_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Circle
        fields = [
            'name', 'description', 'status', 'circle_type',
            'interests', 'member_count', 'created_at', 'last_activity_at'
        ]

    def filter_member_count(self, queryset, name, value):
        """メンバー数でフィルタリング"""
        if value.start is not None:
            queryset = queryset.filter(
                memberships__status='active'
            ).annotate(
                active_members=Count('memberships')
            ).filter(active_members__gte=value.start)

        if value.stop is not None:
            queryset = queryset.filter(
                memberships__status='active'
            ).annotate(
                active_members=Count('memberships')
            ).filter(active_members__lte=value.stop)

        return queryset 