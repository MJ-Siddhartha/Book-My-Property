from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Property, PropertyImage, Amenity
from .forms import PropertyForm, PropertyImageForm, PropertySearchForm
from bookings.models import Booking
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def home(request):
    """Home page with search form"""
    context = {
        'search_form': PropertySearchForm(),
    }
    return render(request, 'properties/home.html', context)

def property_list(request):
    """List all available properties"""
    properties = Property.objects.filter(
        is_available=True, 
        status='available'
    ).order_by('-created_at')
    
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
    if request.user.is_authenticated:
        user_has_booked = Booking.objects.filter(
            property_obj=property_obj,
            guest=request.user,
            status__in=['confirmed', 'completed']
        ).exists()
    
    context = {
        'property': property_obj,
        'images': images,
        'user_has_booked': user_has_booked,
    }
    return render(request, 'properties/property_detail.html', context)

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
