from django import forms
from .models import Property, PropertyImage, Amenity

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'address', 'city', 'state', 
            'zip_code', 'country', 'bedrooms', 'bathrooms', 'max_guests', 
            'square_feet', 'price_per_night', 'price_per_week', 'price_per_month',
            'is_available', 'status', 'instant_booking_enabled', 'amenities'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'price_per_night': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'price_per_week': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'price_per_month': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'amenities': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make amenities field more user-friendly
        self.fields['amenities'].queryset = Amenity.objects.all()
        self.fields['amenities'].help_text = "Select all amenities available at this property"

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Optional caption for this image'}),
        }

class PropertySearchForm(forms.Form):
    PROPERTY_TYPES = [('', 'All Types')] + list(Property.PROPERTY_TYPES)
    
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search properties...'})
    )
    property_type = forms.ChoiceField(
        choices=PROPERTY_TYPES,
        required=False,
        initial=''
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'City'})
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Price', 'min': '0'})
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Price', 'min': '0'})
    )
    bedrooms = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Bedrooms', 'min': '1'})
    )
    guests = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Guests', 'min': '1'})
    )
    check_in = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    check_out = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if check_in and check_out and check_in >= check_out:
            raise forms.ValidationError("Check-out date must be after check-in date.")
        
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError("Minimum price cannot be greater than maximum price.")
        
        return cleaned_data 