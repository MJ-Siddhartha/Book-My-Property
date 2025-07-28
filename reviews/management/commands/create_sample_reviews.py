from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from properties.models import Property
from bookings.models import Booking
from reviews.models import Review
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create sample reviews for testing the rating system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample reviews to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get all properties and users
        properties = Property.objects.all()
        users = User.objects.filter(is_superuser=False)
        
        if not properties.exists():
            self.stdout.write(
                self.style.ERROR('No properties found. Please create some properties first.')
            )
            return
            
        if not users.exists():
            self.stdout.write(
                self.style.ERROR('No users found. Please create some users first.')
            )
            return
        
        reviews_created = 0
        
        for i in range(count):
            # Select random property and user
            property_obj = random.choice(properties)
            user = random.choice(users)
            
            # Check if user already reviewed this property
            if Review.objects.filter(property_obj=property_obj, user=user).exists():
                continue
            
            # Create a completed booking for this user and property (if it doesn't exist)
            past_check_in = timezone.now().date() - timedelta(days=60)
            past_check_out = past_check_in + timedelta(days=10)
            
            try:
                booking = Booking.objects.get(property_obj=property_obj, guest=user)
            except Booking.DoesNotExist:
                booking = Booking(
                    property_obj=property_obj,
                    guest=user,
                    check_in_date=past_check_in,
                    check_out_date=past_check_out,
                    number_of_guests=random.randint(1, 4),
                    total_price=property_obj.price_per_night * 10,
                    price_per_night=property_obj.price_per_night,
                    status='completed',
                    completed_at=past_check_out + timedelta(days=1)
                )
                booking.save()
            
            # Create review
            rating = random.randint(3, 5)  # Mostly positive reviews
            review_titles = [
                "Great experience!",
                "Wonderful stay",
                "Highly recommended",
                "Perfect location",
                "Excellent property",
                "Amazing place",
                "Fantastic stay",
                "Beautiful property",
                "Great value",
                "Lovely accommodation"
            ]
            
            review_comments = [
                "Had a wonderful time staying here. The property was clean and well-maintained.",
                "Great location with easy access to amenities. Would definitely recommend!",
                "The property exceeded our expectations. Very comfortable and spacious.",
                "Perfect for our family vacation. Everything was as described.",
                "Excellent communication with the host. Property was spotless.",
                "Beautiful property in a great neighborhood. Highly recommend!",
                "Had an amazing stay. The property was perfect for our needs.",
                "Great value for money. Clean, comfortable, and well-equipped.",
                "Wonderful experience overall. The host was very helpful.",
                "Lovely property with all the amenities we needed."
            ]
            
            review = Review.objects.create(
                property_obj=property_obj,
                user=user,
                booking=booking,
                rating=rating,
                title=random.choice(review_titles),
                comment=random.choice(review_comments),
                cleanliness_rating=random.randint(3, 5),
                communication_rating=random.randint(3, 5),
                check_in_rating=random.randint(3, 5),
                accuracy_rating=random.randint(3, 5),
                location_rating=random.randint(3, 5),
                value_rating=random.randint(3, 5)
            )
            
            reviews_created += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created review {reviews_created}: {review.title} for {property_obj.title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {reviews_created} sample reviews!')
        ) 