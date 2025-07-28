from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Review CRUD operations
    path('create/<int:property_id>/', views.create_review, name='create_review'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    
    # Review display
    path('property/<int:property_id>/', views.review_list, name='review_list'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    
    # AJAX endpoints
    path('like/<int:review_id>/', views.like_review, name='like_review'),
    path('rating-summary/<int:property_id>/', views.property_rating_summary, name='property_rating_summary'),
] 