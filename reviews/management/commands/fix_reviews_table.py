from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix the reviews table structure by dropping and recreating it'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Drop the existing table
            cursor.execute("DROP TABLE IF EXISTS reviews_review;")
            self.stdout.write(
                self.style.SUCCESS('Dropped existing reviews_review table')
            )
        
        # Run migrations to recreate the table
        from django.core.management import call_command
        call_command('migrate', 'reviews', verbosity=0)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully recreated reviews_review table with correct structure')
        ) 