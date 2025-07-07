from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For Bootstrap icons
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Amenities"

class Property(models.Model):
    PROPERTY_TYPES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('condo', 'Condo'),
        ('studio', 'Studio'),
        ('penthouse', 'Penthouse'),
        ('cottage', 'Cottage'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='United States')
    
    # Property details
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField()
    square_feet = models.PositiveIntegerField(blank=True, null=True)
    
    # Pricing
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_week = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Availability
    is_available = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    instant_booking_enabled = models.BooleanField(default=True)
    
    # Features
    amenities = models.ManyToManyField(Amenity, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.city}"
    
    @property
    def main_image(self):
        """Return the first image or None"""
        return self.images.first()
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def review_count(self):
        """Return number of reviews"""
        return self.reviews.count()

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.property.title} - {self.caption or 'Image'}"
    
    def save(self, *args, **kwargs):
        # If this is marked as primary, unmark others
        if self.is_primary:
            PropertyImage.objects.filter(property=self.property, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
