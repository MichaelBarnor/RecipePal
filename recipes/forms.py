from django import forms
from .models import Recipe
from django.contrib.auth.models import User


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title_text', 'description_text', 'calories_text', 'rating']
        widgets = {
            'title_text': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': True}),
            'calories_text': forms.NumberInput(attrs={'min': 0, 'class': 'form-control', 'required': True}),
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5, 'step': 1, 'class': 'form-control', 'required': True}),
        }

    def clean_calories_text(self):
        calories = self.cleaned_data.get('calories_text')
        if calories is None:
            raise forms.ValidationError("Calories field is required.")
        if calories < 0:
            raise forms.ValidationError("Calories cannot be negative.")
        return calories

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None:
            raise forms.ValidationError("Rating field is required.")
        if not (0 <= rating <= 5):
            raise forms.ValidationError("Rating must be between 0 and 5.")
        return rating


class CollaboratorForm(forms.Form):
    accessible_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        recipe = kwargs.pop('recipe', None)
        super().__init__(*args, **kwargs)
        if recipe:
            self.fields['accessible_users'].queryset = User.objects.exclude(
                id__in=recipe.accessible_users.values_list('id', flat=True)
            ).exclude(id=recipe.creator.id).exclude(groups__name='PMA Administrators')
