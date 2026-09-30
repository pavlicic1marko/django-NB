from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _


class EmailUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=150, label=_("Email"))

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("email",)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        user_model = self._meta.model

        if user_model._default_manager.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("An account with this email already exists."))
        if user_model._default_manager.filter(username__iexact=email).exists():
            raise forms.ValidationError(_("This email is already in use."))

        return email

    def save(self, commit=True):
        self.instance.username = self.cleaned_data["email"]
        # New accounts are inactive until an admin (or an activation flow) enables them.
        self.instance.is_active = False
        return super().save(commit=commit)


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Email or username")