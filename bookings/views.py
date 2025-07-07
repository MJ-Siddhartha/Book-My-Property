from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from .models import Booking
from .forms import BookingForm, BookingCancellationForm
from properties.models import Property

@login_required
def booking_list(request):
    """List user's bookings"""
    if request.user.userprofile.user_type != 'tenant':
        messages.error(request, 'Only tenants can view bookings.')
        return redirect('properties:home')
    
    bookings = Booking.objects.filter(guest=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'today': timezone.now().date(),
    }
    return render(request, 'bookings/booking_list.html', context)

@login_required
def booking_create(request, property_id):
    """Create a new booking"""
    if request.user.userprofile.user_type != 'tenant':
        messages.error(request, 'Only tenants can create bookings.')
        return redirect('properties:property_detail', pk=property_id)
    
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Check if property is available
    if not property_obj.is_available or property_obj.status != 'available':
        messages.error(request, 'This property is not available for booking.')
        return redirect('properties:property_detail', pk=property_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, property_obj=property_obj)
        form.instance.property_obj = property_obj
        if form.is_valid():
            booking = form.save(commit=False)
            booking.guest = request.user
            
            # Check for date conflicts
            conflicting_bookings = Booking.objects.filter(
                property_obj=property_obj,
                check_in_date__lt=booking.check_out_date,
                check_out_date__gt=booking.check_in_date,
                status__in=['confirmed', 'pending']
            )
            
            if conflicting_bookings.exists():
                messages.error(request, 'The selected dates are not available. Please choose different dates.')
            else:
                # Calculate total amount
                nights = (booking.check_out_date - booking.check_in_date).days
                booking.total_amount = nights * property_obj.price_per_night
                booking.status = 'confirmed'  # Instant booking
                booking.save()
                property_obj.is_available = False
                property_obj.status = 'booked'
                property_obj.save()
                messages.success(request, f'Booking confirmed! Your total is ${booking.total_amount}.')
                return redirect('bookings:booking_detail', pk=booking.pk)
    else:
        form = BookingForm(property_obj=property_obj)
        form.instance.property_obj = property_obj
    
    context = {
        'form': form,
        'property': property_obj,
    }
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_detail(request, pk):
    """Show booking details"""
    booking = get_object_or_404(Booking, pk=pk, guest=request.user)
    
    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_detail.html', context)

@login_required
def booking_cancel(request, pk):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, pk=pk, guest=request.user)
    
    # Check if booking can be cancelled
    if booking.status != 'confirmed':
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:booking_detail', pk=booking.pk)
    
    if booking.check_in_date <= timezone.now().date():
        messages.error(request, 'Cannot cancel a booking that has already started.')
        return redirect('bookings:booking_detail', pk=booking.pk)
    
    if request.method == 'POST':
        form = BookingCancellationForm(request.POST, instance=booking)
        if form.is_valid():
            booking.status = 'cancelled'
            booking.cancellation_reason = form.cleaned_data.get('cancellation_reason', '')
            booking.cancelled_at = timezone.now()
            booking.save()
            
            messages.success(request, 'Booking cancelled successfully.')
            return redirect('bookings:booking_list')
    else:
        form = BookingCancellationForm(instance=booking)
    
    context = {
        'form': form,
        'booking': booking,
    }
    return render(request, 'bookings/booking_cancel.html', context)

@login_required
def my_bookings(request):
    """Alias for booking_list"""
    return booking_list(request)
