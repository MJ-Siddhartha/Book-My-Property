from django.db import models
from django.contrib.auth.models import User
from properties.models import Property
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

class Booking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    )
    
    property_obj = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.IntegerField(default=1)
    
    # Pricing
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Additional information
    special_requests = models.TextField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.property_obj.title} - {self.guest.email} ({self.check_in_date} to {self.check_out_date})"
    
    def clean(self):
        """Validate booking dates and availability"""
        if self.check_in_date and self.check_out_date:
            if self.check_in_date >= self.check_out_date:
                raise ValidationError("Check-out date must be after check-in date.")
            
            if self.check_in_date < date.today():
                raise ValidationError("Check-in date cannot be in the past.")
            
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                property_obj=self.property_obj,
                status__in=['confirmed', 'pending'],
                check_in_date__lt=self.check_out_date,
                check_out_date__gt=self.check_in_date
            )
            
            if self.pk:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)
            
            if overlapping_bookings.exists():
                raise ValidationError("This property is already booked for the selected dates.")
    
    def save(self, *args, **kwargs):
        # Only run validation if not updating specific fields
        if not kwargs.get('update_fields'):
            self.clean()
        super().save(*args, **kwargs)
    
    @property
    def duration_nights(self):
        """Calculate the number of nights"""
        return (self.check_out_date - self.check_in_date).days
    
    @property
    def is_active(self):
        """Check if booking is currently active"""
        today = date.today()
        return (self.status == 'confirmed' and 
                self.check_in_date <= today <= self.check_out_date)
    
    @property
    def is_upcoming(self):
        """Check if booking is in the future"""
        return self.status == 'confirmed' and self.check_in_date > date.today()
    
    @property
    def is_past(self):
        """Check if booking is in the past"""
        return self.check_out_date < date.today()
    
    def cancel_booking(self, reason=""):
        """Cancel the booking"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()
    
    def complete_booking(self):
        """Mark booking as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def update_status_based_on_dates(self):
        """Automatically update booking status based on current date"""
        today = date.today()
        
        if self.status == 'confirmed':
            if self.check_out_date < today:
                # Booking has ended, mark as completed
                self.status = 'completed'
                self.completed_at = timezone.now()
                self.save()
                
                # Make property available again
                self.property_obj.is_available = True
                self.property_obj.status = 'available'
                self.property_obj.save()
            elif self.check_in_date <= today <= self.check_out_date:
                # Booking is currently active
                pass  # Keep as confirmed
            elif self.check_in_date > today:
                # Booking is in the future
                pass  # Keep as confirmed
    
    class Meta:
        ordering = ['-created_at']
