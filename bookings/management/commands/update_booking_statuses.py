from django.core.management.base import BaseCommand
from bookings.models import Booking
from properties.models import Property
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Update booking statuses based on current date and fix property availability'

    def handle(self, *args, **options):
        today = date.today()
        updated_bookings = 0
        fixed_properties = 0
        
        # Get all confirmed bookings that have ended
        expired_bookings = Booking.objects.filter(
            status='confirmed',
            check_out_date__lt=today
        )
        
        for booking in expired_bookings:
            booking.status = 'completed'
            booking.completed_at = timezone.now()
            booking.save(update_fields=['status', 'completed_at'])
            
            # Make property available again
            property_obj = booking.property_obj
            property_obj.is_available = True
            property_obj.status = 'available'
            property_obj.save(update_fields=['is_available', 'status'])
            
            updated_bookings += 1
            self.stdout.write(
                self.style.SUCCESS(f'Updated booking {booking.id} to completed and made property available')
            )
        
        # Fix properties that have completed bookings but are still marked as unavailable
        properties_to_fix = Property.objects.filter(
            bookings__status='completed',
            is_available=False
        ).distinct()
        
        for property_obj in properties_to_fix:
            property_obj.is_available = True
            property_obj.status = 'available'
            property_obj.save(update_fields=['is_available', 'status'])
            
            fixed_properties += 1
            self.stdout.write(
                self.style.SUCCESS(f'Fixed property {property_obj.id}: {property_obj.title} - made available')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_bookings} booking statuses and fixed {fixed_properties} properties')
        ) 