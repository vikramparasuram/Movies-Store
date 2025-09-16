from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.NumberInput(attrs={'min':1, 'max':5, 'class':'form-control'}),
            'content': forms.Textarea(attrs={'rows':3, 'class':'form-control'}),
        }
