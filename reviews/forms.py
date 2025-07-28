from django import forms
from .models import Review
from django.core.exceptions import ValidationError

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'rating', 'title', 'comment'
        ]
        widgets = {
            'rating': forms.HiddenInput(),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Write a title for your review'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this property...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get('rating')
        title = cleaned_data.get('title')
        comment = cleaned_data.get('comment')
        
        if not rating:
            raise ValidationError("Please provide an overall rating.")
        
        if not title or len(title.strip()) < 5:
            raise ValidationError("Review title must be at least 5 characters long.")
        
        if not comment or len(comment.strip()) < 20:
            raise ValidationError("Review comment must be at least 20 characters long.")
        
        return cleaned_data

class ReviewEditForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'rating', 'title', 'comment'
        ]
        widgets = {
            'rating': forms.HiddenInput(),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Write a title for your review'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this property...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get('rating')
        title = cleaned_data.get('title')
        comment = cleaned_data.get('comment')
        
        if not rating:
            raise ValidationError("Please provide an overall rating.")
        
        if not title or len(title.strip()) < 5:
            raise ValidationError("Review title must be at least 5 characters long.")
        
        if not comment or len(comment.strip()) < 20:
            raise ValidationError("Review comment must be at least 20 characters long.")
        
        return cleaned_data 