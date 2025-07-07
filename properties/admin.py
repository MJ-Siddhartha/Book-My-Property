from django.contrib import admin
from .models import Property, PropertyImage, Amenity

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'caption', 'is_primary')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name',)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'property_type', 'city', 'price_per_night', 'status', 'is_available', 'created_at')
    list_filter = ('property_type', 'status', 'is_available', 'instant_booking_enabled', 'created_at')
    search_fields = ('title', 'description', 'address', 'city', 'state', 'owner__username', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PropertyImageInline]
    filter_horizontal = ('amenities',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'title', 'description', 'property_type')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'max_guests', 'square_feet')
        }),
        ('Pricing', {
            'fields': ('price_per_night', 'price_per_week', 'price_per_month')
        }),
        ('Availability', {
            'fields': ('is_available', 'status', 'instant_booking_enabled')
        }),
        ('Features', {
            'fields': ('amenities',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'caption', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('property__title', 'caption')
    readonly_fields = ('created_at',)
