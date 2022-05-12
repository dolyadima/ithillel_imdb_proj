from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django import forms
from django.db import transaction
from apps.authentication.models import ActivationToken
from .tasks import send_invitation_email

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "name"]

    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_password2(self):
        if not self.data["password2"] == self.data["password"]:
            raise forms.ValidationError(_("Passwords mismatch"))

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.is_active = False
            user.set_password(self.data["password"])
            user.save()
            activation_token = ActivationToken.objects.create(user=user)
            transaction.on_commit(
                lambda: send_invitation_email.delay(activation_token.id)
            )
        return user
