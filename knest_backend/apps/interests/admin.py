from django.contrib import admin
from .models import InterestCategory, InterestSubcategory, InterestTag, UserInterestProfile

@admin.register(InterestCategory)
class InterestCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at')
    list_filter = ('type',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(InterestSubcategory)
class InterestSubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'category__name')
    ordering = ('category__name', 'name')

@admin.register(InterestTag)
class InterestTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'usage_count', 'created_at')
    list_filter = ('subcategory__category', 'subcategory')
    search_fields = ('name', 'description', 'subcategory__name', 'subcategory__category__name')
    ordering = ('-usage_count', 'subcategory__category__name', 'subcategory__name', 'name')

@admin.register(UserInterestProfile)
class UserInterestProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'subcategory', 'tag', 'level', 'added_at')
    list_filter = ('level', 'category', 'subcategory', 'tag')
    search_fields = ('user__username', 'category__name', 'subcategory__name', 'tag__name')
    ordering = ('-added_at',) 