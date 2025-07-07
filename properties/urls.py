from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.home, name='home'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/create/', views.property_create, name='property_create'),
    path('properties/<int:pk>/edit/', views.property_update, name='property_update'),
    path('properties/<int:pk>/delete/', views.property_delete, name='property_delete'),
    path('my-properties/', views.my_properties, name='my_properties'),
    path('search/', views.property_search, name='property_search'),
    path('properties/image/<int:image_id>/delete/', views.property_image_delete, name='property_image_delete'),
] 