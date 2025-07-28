# BookMyProperty

A Django-based property booking platform where owners can list properties and tenants can book them.

## Features

- User authentication (owner/tenant)
- List, edit, and delete properties (owners)
- Book properties (tenants)
- Profile management with avatar upload
- Booking history and cancellation
- Responsive Bootstrap UI

## Setup

1. **Clone the repo:**
   ```sh
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Create a virtual environment and activate it:**
   ```sh
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```

5. **Create a superuser (optional):**
   ```sh
   python manage.py createsuperuser
   ```

6. **Run the server:**
   ```sh
   python manage.py runserver
   ```

7. **Access the app:**
   - Go to [http://localhost:8000/](http://localhost:8000/)

## Default Credentials

- No default users. Sign up as owner or tenant.

## Notes

- Media uploads (avatars, property images) are stored in `/media/`.
- Static files are managed by Django's staticfiles app.
- All prices are displayed in Indian Rupees (₹).

## Testing the Ratings System

To create sample ratings for testing:

```bash
python manage.py create_sample_ratings --count 20
```

This will create sample ratings for testing the rating system.

## Managing Booking Statuses

To automatically update booking statuses based on dates:

```bash
python manage.py update_booking_statuses
```

This will mark completed bookings as 'completed' based on their check-out dates. 