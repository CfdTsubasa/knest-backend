from django.contrib import admin
from .models import Interest, UserInterest, InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_official', 'usage_count', 'created_at']
    list_filter = ['category', 'is_official', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-usage_count', 'name']

@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ['user', 'interest', 'added_at']
    list_filter = ['added_at', 'interest__category']
    search_fields = ['user__username', 'interest__name']
    ordering = ['-added_at']

@admin.register(InterestCategory)
class InterestCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(InterestSubcategory)
class InterestSubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    ordering = ['category__name', 'name']

@admin.register(InterestTag)
class InterestTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcategory', 'usage_count', 'created_at']
    list_filter = ['subcategory__category', 'created_at']
    search_fields = ['name', 'description', 'subcategory__name']
    ordering = ['-usage_count', 'subcategory__category__name', 'subcategory__name', 'name']

@admin.register(UserInterestProfile)
class UserInterestProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'level', 'added_at']
    list_filter = ['level', 'category', 'added_at']
    search_fields = ['user__username', 'category__name', 'subcategory__name', 'tag__name']
    ordering = ['-added_at']
    
    def display_name(self, obj):
        return obj.display_name
    display_name.short_description = '表示名' 