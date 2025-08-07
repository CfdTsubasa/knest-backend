from django_filters import rest_framework as filters
from .models import InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile

class InterestCategoryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    type = filters.CharFilter(lookup_expr='exact')
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = InterestCategory
        fields = ['name', 'type', 'created_at']

class InterestSubcategoryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.UUIDFilter(field_name='category__id')
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = InterestSubcategory
        fields = ['name', 'category', 'created_at']

class InterestTagFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    subcategory = filters.UUIDFilter(field_name='subcategory__id')
    category = filters.UUIDFilter(field_name='subcategory__category__id')
    min_usage_count = filters.NumberFilter(field_name='usage_count', lookup_expr='gte')
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = InterestTag
        fields = ['name', 'subcategory', 'category', 'usage_count', 'created_at']

class UserInterestProfileFilter(filters.FilterSet):
    category = filters.UUIDFilter(field_name='category__id')
    subcategory = filters.UUIDFilter(field_name='subcategory__id')
    tag = filters.UUIDFilter(field_name='tag__id')
    level = filters.NumberFilter()
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UserInterestProfile
        fields = ['category', 'subcategory', 'tag', 'level', 'created_at'] 