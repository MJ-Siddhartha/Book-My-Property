from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property_obj', 'guest', 'check_in_date', 'check_out_date', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'check_in_date', 'check_out_date', 'created_at')
    search_fields = ('property_obj__title', 'guest__username', 'guest__email', 'property_obj__city')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('property_obj', 'guest', 'check_in_date', 'check_out_date', 'number_of_guests')
        }),
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Status', {
            'fields': ('status', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirm_bookings', 'cancel_bookings', 'complete_bookings']
    
    def confirm_bookings(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} bookings have been confirmed.')
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} bookings have been cancelled.')
    cancel_bookings.short_description = "Cancel selected bookings"
    
    def complete_bookings(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} bookings have been completed.')
    complete_bookings.short_description = "Complete selected bookings"
