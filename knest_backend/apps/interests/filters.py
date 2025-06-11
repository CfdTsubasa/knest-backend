from django_filters import rest_framework as filters
from .models import Interest, UserInterest

class InterestFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateTimeFromToRangeFilter()
    min_usage_count = filters.NumberFilter(field_name='usage_count', lookup_expr='gte')
    max_usage_count = filters.NumberFilter(field_name='usage_count', lookup_expr='lte')

    class Meta:
        model = Interest
        fields = ['name', 'description', 'is_official', 'created_at']

class UserInterestFilter(filters.FilterSet):
    interest_name = filters.CharFilter(field_name='interest__name', lookup_expr='icontains')
    level = filters.RangeFilter()
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UserInterest
        fields = ['interest', 'level', 'created_at'] 