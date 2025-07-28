from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from properties.models import Property
from bookings.models import Booking
from django.core.exceptions import ValidationError
from django.utils import timezone

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    property_obj = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    
    # Rating and review content
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Additional rating categories
    cleanliness_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    communication_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    check_in_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    accuracy_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    location_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    value_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Likes
    likes = models.ManyToManyField(User, related_name='liked_reviews', blank=True)
    
    class Meta:
        unique_together = ['property_obj', 'user']
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        return f"{self.property_obj.title} - {self.user.username} ({self.rating}/5)"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    @property
    def overall_rating(self):
        """Calculate overall rating from all rating categories"""
        ratings = [
            self.rating,
            self.cleanliness_rating,
            self.communication_rating,
            self.check_in_rating,
            self.accuracy_rating,
            self.location_rating,
            self.value_rating
        ]
        
        # Filter out None values
        valid_ratings = [r for r in ratings if r is not None]
        
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return self.rating
    
    @property
    def rating_stars(self):
        """Return rating as stars (★★★★☆)"""
        full_stars = '★' * self.rating
        empty_stars = '☆' * (5 - self.rating)
        return full_stars + empty_stars
    
    @property
    def is_recent(self):
        """Check if review was posted within last 30 days"""
        return (timezone.now() - self.created_at).days <= 30
