from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from properties.models import Property
from reviews.models import Review
import random

class Command(BaseCommand):
    help = 'Create sample ratings for testing the rating system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample ratings to create'
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
        
        ratings_created = 0
        
        for i in range(count):
            # Select random property and user
            property_obj = random.choice(properties)
            user = random.choice(users)
            
            # Check if user already rated this property
            if Review.objects.filter(property_obj=property_obj, user=user).exists():
                continue
            
            # Create rating
            rating = random.randint(3, 5)  # Mostly positive ratings
            rating_titles = [
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
            
            rating_comments = [
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
                rating=rating,
                title=random.choice(rating_titles),
                comment=random.choice(rating_comments),
                cleanliness_rating=random.randint(3, 5),
                communication_rating=random.randint(3, 5),
                check_in_rating=random.randint(3, 5),
                accuracy_rating=random.randint(3, 5),
                location_rating=random.randint(3, 5),
                value_rating=random.randint(3, 5)
            )
            
            ratings_created += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created rating {ratings_created}: {review.title} for {property_obj.title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {ratings_created} sample ratings!')
        ) 