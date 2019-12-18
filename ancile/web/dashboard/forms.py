from django import forms
from ancile.web.dashboard.models import *
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.postgres.fields import JSONField

class AdminAddPolicyForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)
    provider = forms.ChoiceField(label="Provider")
    active = forms.BooleanField(label="Active?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminAddPolicyForm, self).__init__(*args, **kwargs)
        app_choices = [(app.name, app.name) for app in App.objects.all()]
        self.fields['app'] = forms.ChoiceField(label="App", choices=app_choices)

class AdminEditPolicyForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)
    active = forms.BooleanField(label="Active?", required=False)

class AdminEditUserForm(forms.Form):
    is_developer = forms.BooleanField(label="Developer?", required=False)
    is_admin = forms.BooleanField(label="Admin?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        choices = [(app.name, app.name) for app in App.objects.all()]
        self.fields['apps'] = forms.MultipleChoiceField(label="Developer For", required=False, choices=choices)

class AdminEditAppForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")

    def __init__(self, *args, **kwargs):
        super(AdminEditAppForm, self).__init__(*args, **kwargs)
        choices = [(user.username, user.username) for user in User.objects.filter(is_developer=True)]
        self.fields['developers'] = forms.MultipleChoiceField(label="Developers", choices=choices)

class AdminAddGroupForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminAddGroupForm, self).__init__(*args, **kwargs)
        choices = [(scope.value, scope.simple_name) for scope in Scope.objects.all()]
        self.fields['scopes'] = forms.MultipleChoiceField(label="Scopes", choices=choices)

class AdminEditGroupForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminEditGroupForm, self).__init__(*args, **kwargs)
        choices = [(scope.value, scope.simple_name) for scope in Scope.objects.all()]
        self.fields['scopes'] = forms.MultipleChoiceField(label="Scopes", choices=choices)

class AdminAddFunctionForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)
    body = forms.CharField(label="Code", widget=forms.Textarea)

class AdminEditFunctionForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)
    body = forms.CharField(label="Code", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(AdminEditFunctionForm, self).__init__(*args, **kwargs)
        choices = [(app.id, app.name) for app in App.objects.all()]
        self.fields['app_id'] = forms.ChoiceField(label="App", choices=choices)

class AdminAddPolicyTemplateForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(AdminAddPolicyTemplateForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class AdminEditPolicyTemplateForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(AdminEditPolicyTemplateForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class AdminAddProviderForm(forms.Form):
    path_name = forms.CharField(label="Path Name")
    display_name = forms.CharField(label="Display Name")
    token_url = forms.CharField(label="Access Token URL")
    auth_url = forms.CharField(label="Authorize URL")
    client_id = forms.CharField(label="Client ID")
    client_secret = forms.CharField(label="Client Secret")
    json = forms.CharField(label="Extra Paramaters", widget=forms.Textarea)

class AdminAddScopeForm(forms.Form):
    simple_name = forms.CharField(label="Display Name")
    value = forms.CharField(label="Value")
    description = forms.CharField(label="Description")

class AdminEditScopeForm(AdminAddScopeForm):
    def __init__(self, *args, **kwargs):
        super(AdminEditScopeForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class DevEditAppForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")

    def __init__(self, *args, **kwargs):
        super(DevEditAppForm, self).__init__(*args, **kwargs)
        choices = [(user.username, user.username) for user in User.objects.all() if user.is_developer]
        self.fields['developers'] = forms.MultipleChoiceField(label="Developers", choices=choices)


class DevEditGroupForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")

    def __init__(self, *args, **kwargs):
        super(DevEditGroupForm, self).__init__(*args, **kwargs)
        choices = [(scope.value, scope.simple_name) for scope in Scope.objects.all()]
        self.fields['scopes'] = forms.MultipleChoiceField(label="Scopes", choices=choices)

class DevEditPolicyTemplateForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(DevEditPolicyTemplateForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class DevEditFunctionForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    body = forms.CharField(label="Code", widget=forms.Textarea)

class UserEditDataForm(forms.Form):
    json = forms.CharField(label="Data")

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", )

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserSettingsForm(forms.ModelForm):
    old_password = forms.CharField(label='Current password', widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(label='New password', widget=forms.PasswordInput, required=False)
    new_password_confirm = forms.CharField(label='New password confirmation', widget=forms.PasswordInput, required=False)
    email = forms.CharField(label='Email', widget=forms.Textarea, required=True)
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(UserSettingsForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]

        if email == self.request.user.email:
            return email
        elif User.objects.filter(email=email):
            raise forms.ValidationError("* User with this email already exists.")
        return email

    def clean_new_password_confirm(self):
        # Check that the two password entries match
        old_password = self.cleaned_data.get("old_password")
        new_password = self.cleaned_data.get("new_password")
        new_password_confirm = self.cleaned_data.get("new_password_confirm")

        if old_password:
            if authenticate(username=self.request.user, password=old_password):
                if new_password or new_password_confirm:
                    if new_password != new_password_confirm:
                        raise forms.ValidationError("Passwords don't match.")
                    return new_password_confirm
                elif not new_password and not new_password_confirm:
                    raise forms.ValidationError("New password can't be blank.")
            raise forms.ValidationError("Old password is not valid.")
        return ""

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = self.request.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if user.email != self.cleaned_data["email"]:
            user.email = self.cleaned_data["email"]
        if self.cleaned_data["new_password_confirm"]:
            user.set_password(self.cleaned_data["new_password_confirm"])
        if commit:
            user.save()
        return user