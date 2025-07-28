from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Property, PropertyImage, Amenity
from .forms import PropertyForm, PropertyImageForm, PropertySearchForm
from bookings.models import Booking
from reviews.models import Review
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import calendar

def home(request):
    """Home page with search form"""
    context = {
        'search_form': PropertySearchForm(),
    }
    return render(request, 'properties/home.html', context)

def property_list(request):
    """List all properties with availability information"""
    properties = Property.objects.all().order_by('-created_at')
    
    # Apply search filters
    search_form = PropertySearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        property_type = search_form.cleaned_data.get('property_type')
        city = search_form.cleaned_data.get('city')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        bedrooms = search_form.cleaned_data.get('bedrooms')
        guests = search_form.cleaned_data.get('guests')
        
        if search:
            properties = properties.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(city__icontains=search) |
                Q(state__icontains=search)
            )
        
        if property_type:
            properties = properties.filter(property_type=property_type)
        
        if city:
            properties = properties.filter(city__icontains=city)
        
        if min_price:
            properties = properties.filter(price_per_night__gte=min_price)
        
        if max_price:
            properties = properties.filter(price_per_night__lte=max_price)
        
        if bedrooms:
            properties = properties.filter(bedrooms__gte=bedrooms)
        
        if guests:
            properties = properties.filter(max_guests__gte=guests)
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'search_form': search_form,
    }
    return render(request, 'properties/property_list.html', context)

def property_detail(request, pk):
    """Show property details"""
    property_obj = get_object_or_404(Property, pk=pk)
    images = property_obj.images.all()
    
    # Check if user has already booked this property
    user_has_booked = False
    user_bookings = []
    user_has_reviewed = False
    user_review = None
    
    if request.user.is_authenticated:
        user_bookings = Booking.objects.filter(
            property_obj=property_obj,
            guest=request.user
        ).order_by('-created_at')
        
        user_has_booked = user_bookings.exists()
        
        # Check if user has reviewed this property
        user_review = Review.objects.filter(
            property_obj=property_obj,
            user=request.user
        ).first()
        user_has_reviewed = user_review is not None
    
    # Get current and upcoming bookings for this property
    current_bookings = Booking.objects.filter(
        property_obj=property_obj,
        status__in=['confirmed', 'pending']
    ).order_by('check_in_date')
    
    context = {
        'property': property_obj,
        'images': images,
        'user_has_booked': user_has_booked,
        'user_bookings': user_bookings,
        'user_has_reviewed': user_has_reviewed,
        'user_review': user_review,
        'can_review': request.user.is_authenticated and user_has_booked,
        'current_bookings': current_bookings,
    }
    return render(request, 'properties/property_detail.html', context)

def property_calendar(request, pk):
    """Show property availability calendar"""
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Get current month and year
    today = datetime.now()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Create calendar
    cal = calendar.monthcalendar(year, month)
    
    # Get all bookings for this property in the current month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    bookings = Booking.objects.filter(
        property_obj=property_obj,
        check_in_date__lte=end_date,
        check_out_date__gte=start_date,
        status__in=['confirmed', 'pending']
    )
    
    # Create availability data for each day
    availability_data = {}
    for day in range(1, end_date.day + 1):
        current_date = datetime(year, month, day).date()
        
        # Check if this date is booked
        is_booked = bookings.filter(
            check_in_date__lte=current_date,
            check_out_date__gt=current_date
        ).exists()
        
        availability_data[day] = {
            'date': current_date,
            'is_booked': is_booked,
            'is_today': current_date == today.date(),
            'is_past': current_date < today.date(),
        }
    

    
    # Create a list of calendar weeks with availability data
    calendar_with_availability = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'is_booked': False, 'is_today': False, 'is_past': False})
            else:
                day_data = availability_data.get(day, {})
                week_data.append({
                    'day': day,
                    'is_booked': day_data.get('is_booked', False),
                    'is_today': day_data.get('is_today', False),
                    'is_past': day_data.get('is_past', False)
                })
        calendar_with_availability.append(week_data)
    
    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'property': property_obj,
        'calendar': calendar_with_availability,
        'availability_data': availability_data,
        'current_year': year,
        'current_month': month,
        'month_name': calendar.month_name[month],
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': today.date(),
    }
    return render(request, 'properties/property_calendar.html', context)

@login_required
def property_create(request):
    """Create a new property"""
    if request.user.userprofile.user_type != 'owner':
        messages.error(request, 'Only property owners can create listings.')
        return redirect('properties:property_list')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle multiple images
            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image
                )
            
            messages.success(request, 'Property created successfully!')
            return redirect('properties:property_detail', pk=property_obj.pk)
    else:
        form = PropertyForm()
    
    context = {
        'form': form,
        'title': 'Add New Property',
    }
    return render(request, 'properties/property_form.html', context)

@login_required
def property_update(request, pk):
    """Update an existing property"""
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.user.userprofile.user_type != 'owner':
        messages.error(request, 'Only property owners can update listings.')
        return redirect('properties:property_list')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            
            # Handle additional images
            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image
                )
            
            messages.success(request, 'Property updated successfully!')
            return redirect('properties:property_detail', pk=property_obj.pk)
    else:
        form = PropertyForm(instance=property_obj)
    
    context = {
        'form': form,
        'property': property_obj,
        'title': 'Edit Property',
    }
    return render(request, 'properties/property_form.html', context)

@login_required
def property_delete(request, pk):
    """Delete a property"""
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, 'Property deleted successfully!')
        return redirect('properties:my_properties')
    
    context = {
        'property': property_obj,
    }
    return render(request, 'properties/property_confirm_delete.html', context)

@login_required
def my_properties(request):
    """Show user's properties"""
    if request.user.userprofile.user_type != 'owner':
        messages.error(request, 'Only property owners can view their properties.')
        return redirect('properties:property_list')
    
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'properties': properties,
    }
    return render(request, 'properties/my_properties.html', context)

def property_search(request):
    """Advanced property search"""
    search_form = PropertySearchForm(request.GET)
    properties = Property.objects.filter(is_available=True, status='available')
    
    if search_form.is_valid():
        # Apply search filters (same logic as property_list)
        search = search_form.cleaned_data.get('search')
        property_type = search_form.cleaned_data.get('property_type')
        city = search_form.cleaned_data.get('city')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        bedrooms = search_form.cleaned_data.get('bedrooms')
        guests = search_form.cleaned_data.get('guests')
        
        if search:
            properties = properties.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(city__icontains=search) |
                Q(state__icontains=search)
            )
        
        if property_type:
            properties = properties.filter(property_type=property_type)
        
        if city:
            properties = properties.filter(city__icontains=city)
        
        if min_price:
            properties = properties.filter(price_per_night__gte=min_price)
        
        if max_price:
            properties = properties.filter(price_per_night__lte=max_price)
        
        if bedrooms:
            properties = properties.filter(bedrooms__gte=bedrooms)
        
        if guests:
            properties = properties.filter(max_guests__gte=guests)
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'search_form': search_form,
    }
    return render(request, 'properties/property_search.html', context)

@login_required
@require_POST
def property_image_delete(request, image_id):
    image = get_object_or_404(PropertyImage, id=image_id, property__owner=request.user)
    image.delete()
    return JsonResponse({'success': True})
