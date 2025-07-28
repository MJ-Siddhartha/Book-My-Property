from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.urls import reverse
from .models import Review
from .forms import ReviewForm, ReviewEditForm
from properties.models import Property
from bookings.models import Booking

@login_required
def create_review(request, property_id):
    """Create a new review for a property"""
    property_obj = get_object_or_404(Property, id=property_id)
    
    # Check if user has already reviewed this property
    existing_review = Review.objects.filter(property_obj=property_obj, user=request.user).first()
    if existing_review:
        messages.warning(request, "You have already reviewed this property.")
        return redirect('properties:property_detail', pk=property_id)
    
    # Check if user has any bookings for this property (confirmed or completed)
    user_bookings = Booking.objects.filter(
        property_obj=property_obj,
        guest=request.user,
        status__in=['confirmed', 'completed']
    )
    
    if not user_bookings.exists():
        messages.error(request, "You can only review properties you have booked.")
        return redirect('properties:property_detail', pk=property_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property_obj = property_obj
            review.user = request.user
            review.save()
            
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('properties:property_detail', pk=property_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'property': property_obj,
        'user_bookings': user_bookings
    }
    return render(request, 'reviews/create_review.html', context)

@login_required
def edit_review(request, review_id):
    """Edit an existing review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewEditForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated successfully!")
            return redirect('properties:property_detail', pk=review.property_obj.id)
    else:
        form = ReviewEditForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'property': review.property_obj
    }
    return render(request, 'reviews/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    property_id = review.property_obj.id
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Your review has been deleted successfully!")
        return redirect('properties:property_detail', pk=property_id)
    
    context = {
        'review': review,
        'property': review.property_obj
    }
    return render(request, 'reviews/delete_review.html', context)

def review_list(request, property_id):
    """Display all reviews for a property"""
    property_obj = get_object_or_404(Property, id=property_id)
    reviews = Review.objects.filter(property_obj=property_obj).select_related('user')
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate rating statistics
    rating_stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()
    
    context = {
        'property': property_obj,
        'page_obj': page_obj,
        'rating_stats': rating_stats,
        'rating_distribution': rating_distribution,
        'can_review': False
    }
    
    if request.user.is_authenticated:
        # Check if user can review this property
        has_reviewed = Review.objects.filter(property_obj=property_obj, user=request.user).exists()
        has_booked = Booking.objects.filter(
            property_obj=property_obj,
            guest=request.user,
            status__in=['confirmed', 'completed']
        ).exists()
        
        context['can_review'] = not has_reviewed and has_booked
        context['has_reviewed'] = has_reviewed
    
    return render(request, 'reviews/review_list.html', context)

@login_required
def my_reviews(request):
    """Display user's own reviews"""
    reviews = Review.objects.filter(user=request.user).select_related('property_obj')
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'reviews': reviews
    }
    return render(request, 'reviews/my_reviews.html', context)

@require_POST
@login_required
def like_review(request, review_id):
    """Like/unlike a review (AJAX)"""
    review = get_object_or_404(Review, id=review_id)
    
    if request.user in review.likes.all():
        review.likes.remove(request.user)
        liked = False
    else:
        review.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': review.likes.count()
    })

def property_rating_summary(request, property_id):
    """Get rating summary for a property (AJAX)"""
    property_obj = get_object_or_404(Property, id=property_id)
    reviews = Review.objects.filter(property_obj=property_obj)
    
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        total_reviews = reviews.count()
        
        # Rating distribution
        distribution = {}
        for i in range(1, 6):
            distribution[i] = reviews.filter(rating=i).count()
        
        return JsonResponse({
            'avg_rating': round(avg_rating, 1),
            'total_reviews': total_reviews,
            'distribution': distribution
        })
    
    return JsonResponse({
        'avg_rating': 0,
        'total_reviews': 0,
        'distribution': {}
    })
