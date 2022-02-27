from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from . import models

# ratings use in Reviews
rating_values = [
    ('1', 1),
    ('2', 2),
    ('3', 3),
    ('4', 4),
    ('5', 5)
]


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)  


class ReviewForm(forms.ModelForm):
    post_review = forms.BooleanField(widget=forms.HiddenInput, initial=True)
    rating = forms.ChoiceField(choices=rating_values, widget=forms.RadioSelect)

    class Meta:
        model = models.Review
        fields = ['rating', 'headline', 'body']


class TicketForm(forms.ModelForm):
    post_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = models.Ticket
        fields = ['title', 'description', 'image']
