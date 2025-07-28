from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'property_obj', 'user', 'rating', 'title', 
        'created_at', 'is_recent'
    ]
    list_filter = [
        'rating', 'created_at', 'property_obj__city',
        'property_obj__property_type'
    ]
    search_fields = [
        'title', 'comment', 'user__username', 
        'user__email', 'property_obj__title'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('property_obj', 'user')
        }),
        ('Review Content', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('Detailed Ratings', {
            'fields': (
                'cleanliness_rating', 'communication_rating', 
                'check_in_rating', 'accuracy_rating', 
                'location_rating', 'value_rating'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_recent(self, obj):
        return obj.is_recent
    is_recent.boolean = True
    is_recent.short_description = 'Recent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'property_obj')
