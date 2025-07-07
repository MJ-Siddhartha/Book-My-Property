from django import forms
from .models import Booking
from properties.models import Property
from datetime import date, timedelta

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'number_of_guests', 'special_requests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'min': (date.today() + timedelta(days=1)).isoformat()}),
            'number_of_guests': forms.NumberInput(attrs={'min': '1'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requests or requirements...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.property_obj = kwargs.pop('property_obj', None)
        super().__init__(*args, **kwargs)
        
        if self.property_obj:
            # Set max guests based on property capacity
            self.fields['number_of_guests'].widget.attrs['max'] = self.property_obj.max_guests
            self.fields['number_of_guests'].help_text = f"Maximum {self.property_obj.max_guests} guests allowed"
    
    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        number_of_guests = cleaned_data.get('number_of_guests')
        
        if check_in_date and check_out_date:
            if check_in_date >= check_out_date:
                raise forms.ValidationError("Check-out date must be after check-in date.")
            
            if check_in_date < date.today():
                raise forms.ValidationError("Check-in date cannot be in the past.")
            
            # Check for overlapping bookings
            if self.property_obj:
                overlapping_bookings = Booking.objects.filter(
                    property_obj=self.property_obj,
                    status__in=['confirmed', 'pending'],
                    check_in_date__lt=check_out_date,
                    check_out_date__gt=check_in_date
                )
                
                if self.instance.pk:
                    overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
                
                if overlapping_bookings.exists():
                    raise forms.ValidationError("This property is already booked for the selected dates.")
        
        if number_of_guests and self.property_obj and number_of_guests > self.property_obj.max_guests:
            raise forms.ValidationError(f"Maximum {self.property_obj.max_guests} guests allowed for this property.")
        
        return cleaned_data
    
    def save(self, commit=True):
        booking = super().save(commit=False)
        
        if self.property_obj:
            booking.property_obj = self.property_obj
            booking.price_per_night = self.property_obj.price_per_night
            booking.total_price = booking.price_per_night * booking.duration_nights
        
        if commit:
            booking.save()
        
        return booking

class BookingCancellationForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for cancellation (optional)...'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        self.booking = kwargs.pop('booking', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.booking:
            if self.booking.status != 'confirmed':
                raise forms.ValidationError("Only confirmed bookings can be cancelled.")
            
            if self.booking.check_in_date <= date.today():
                raise forms.ValidationError("Cannot cancel bookings that have already started.")
        
        return cleaned_data 