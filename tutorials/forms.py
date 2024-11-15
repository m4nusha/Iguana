"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Booking, Session

from .models import Student


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user


class StudentForm(forms.ModelForm):
    """Form to create or update students"""
    class Meta:
        model = Student
        fields = ['name', 'username', 'email', 'allocated']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        allocated = cleaned_data.get('allocated')

        # Get the current student instance ID if updating, otherwise None
        student_id = self.instance.id if self.instance and self.instance.id else None

        # Case-insensitive email validation
        if email:
            student_id = self.instance.id if self.instance else None
            # Ensure email is unique, case insensitive, excluding the current student's email
            if Student.objects.exclude(id=student_id).filter(email=email.lower()).exists():
                self.add_error('email', "A student with this email already exists.")
            # Normalize email to lowercase
            cleaned_data['email'] = email.lower()

        # Ensure username is unique (excluding the current student's username)
        if username:
            if Student.objects.exclude(id=student_id).filter(username=username).exists():
                self.add_error('username', "This username is already taken.")

        # Boolean validation for allocated
        if allocated is not None:
            if isinstance(allocated, bool):
                pass  # Valid boolean value
            else:
                self.add_error('allocated', "Allocated must be a boolean value.")

        return cleaned_data

class BookingForm(forms.ModelForm):
    """Form to create or update a booking."""

    class Meta:
        model = Booking
        fields = ['term', 'student', 'tutor']


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            'session_date', 
            'session_time', 
            'duration', 
            'lesson_type', 
            'venue', 
            'amount', 
            'payment_status'
        ]
