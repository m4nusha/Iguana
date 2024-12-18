from datetime import date, datetime
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import Student, StudentRequest, Tutor, Subject, User, Booking, Session
from django.core.exceptions import ValidationError


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

            # ensure "@johndoe" is admin
            if user:
                if username == '@johndoe':
                    if user.user_type != 'admin':
                        user.user_type = 'admin'
                        user.save()
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'user_type']


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

    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.Select)

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'user_type']

    def save(self):
        """Create a new user."""
        super().save(commit=False)

        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            user_type=self.cleaned_data.get('user_type')
        )
        return user
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'user_type']


class CreateUserForm(forms.ModelForm):
    user_type = forms.ChoiceField(
        choices=[('student', 'Student'), ('tutor', 'Tutor')],
        initial='student',  # Default to 'student'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
            if user_type == 'student':
                Student.objects.create(username=user)
            elif user_type == 'tutor':
                Tutor.objects.create(username=user)
        return user

class TutorForm(forms.ModelForm):
    """Form for creating and updating tutors."""

    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Tutor
        fields = ['name', 'username', 'email','subjects', 'rate']
        rate = forms.DecimalField(max_digits=6, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            default_subject = Subject.objects.get(name = "Python")
            if not self.instance.pk: 
                self.fields['subjects'].initial = [default_subject.id]
        except Subject.DoesNotExist:
            pass

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')

        #get the current tutor instance ID if updating otherwise none
        tutor_id = self.instance.id if self.instance and self.instance.id else None

        #case insensitive email validation
        if email:
            tutor_id = self.instance.id if self.instance else None
            #ensure that email is unique, case insensitive, excluding the current tutor's email
            if Tutor.objects.exclude(id=tutor_id).filter(email=email.lower()).exists():
                self.add_error('email', "A tutor with this email already exists.")
            #normalise email to lowercase
            cleaned_data['email'] = email.lower()

        #ensure username is unique (excluding the current tutor's username)
        if username:
            tutor_id = self.instance.id if self.instance else None
            if Tutor.objects.exclude(id=tutor_id).filter(username=username).exists():
                self.add_error('username', "This username is already taken.")
            cleaned_data['username'] = username

        return cleaned_data
    
    def save(self, commit=True):
        """Override save method to ensure default subject is assigned."""
        tutor = super().save(commit=False)
        if commit:
            tutor.save()  
            tutor.subjects.set(self.cleaned_data['subjects'])

            if not tutor.subjects.exists():
                python_subject, created = Subject.objects.get_or_create(name="Python")
                tutor.subjects.add(python_subject)
        return tutor

class StudentForm(forms.ModelForm):
    """Form to create or update students"""
    class Meta:
        model = Student
        fields = ['name', 'username', 'email', 'allocated', 'payment']

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

        if username:
            # If username is passed as an ID, retrieve the User instance
            if isinstance(username, int):
                username = User.objects.get(id=username)

            # Check for uniqueness
            if Student.objects.exclude(id=student_id).filter(username=username).exists():
                self.add_error('username', "This user is already associated with another student.")

        if allocated is not None:
            if isinstance(allocated, bool):
                pass  # Valid boolean value
            else:
                self.add_error('allocated', "Allocated must be a boolean value.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class StudentRequestForm(forms.ModelForm):
    """Form to create or update student requests"""
    class Meta:
        model = StudentRequest
        fields = ['username', 'request_type', 'description', 'status', 'priority']

    def save(self, commit=True):
        instance = super().save(commit=False)  # Get the instance without saving to the database yet
        instance.name = instance.username.get_full_name()  # Populate the name based on the username
        if commit:
            instance.save()  
        return instance

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        request_type = cleaned_data.get('request_type')

        # Get the current instance ID if updating, otherwise None
        instance_id = self.instance.id if self.instance else None

        # Ensure uniqueness of request_type for the same username, excluding the current instance
        if StudentRequest.objects.exclude(id=instance_id).filter(username=username, request_type=request_type).exists():
            self.add_error(
                'request_type',
                f"A request of this type already exists for user @{username}."
            )

        return cleaned_data


class BookingForm(forms.ModelForm):
    """Form to create or update a booking."""
    class Meta:
        model = Booking
        fields = ['term','lesson_type', 'student', 'tutor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['student'].queryset = Student.objects.all()
        self.fields['student'].label_from_instance = lambda obj: obj.username.username
        self.fields['tutor'].queryset = Tutor.objects.all()
        self.fields['tutor'].label_from_instance = lambda obj: obj.username.username

    def clean(self):
        cleaned_data = super().clean()
        term = cleaned_data.get('term')
        lesson_type = cleaned_data.get('lesson_type')
        student = cleaned_data.get('student')
        tutor = cleaned_data.get('tutor')

        if student and not Student.objects.filter(id=student.id).exists():
            self.add_error('student', 'Student does not exist.')
        if tutor and not Tutor.objects.filter(id=tutor.id).exists():
            self.add_error('tutor', 'Tutor does not exist.')
        if student == tutor:
            self.add_error('tutor', 'A student cannot book themselves as a tutor.')
            self.add_error('student', 'A student cannot book themselves as a tutor.')
        if Booking.objects.filter(term=term, lesson_type=lesson_type, student=student, tutor=tutor).exists():
            raise ValidationError('A booking with the same details already exists.')
        
        return cleaned_data
    

class UpdateBookingForm(forms.ModelForm):
    """Form to update an existing booking."""
    class Meta:
        model = Booking
        fields = ['term','lesson_type', 'student', 'tutor']

    def clean(self):
        cleaned_data = super().clean()
        term = cleaned_data.get('term')
        lesson_type = cleaned_data.get('lesson_type')
        student = cleaned_data.get('student')
        tutor = cleaned_data.get('tutor')

        if student is None:
            raise ValidationError("Student must be selected.")
        if tutor is None:
            raise ValidationError("Tutor must be selected.")
        if not Student.objects.filter(id=student.id).exists():
            self.add_error('student', 'The selected student does not exist.')
        if not Tutor.objects.filter(id=tutor.id).exists():
            self.add_error('tutor', 'The selected tutor does not exist.')
        if student == tutor:
            self.add_error('tutor', 'The student and tutor cannot be the same person.')
        if Booking.objects.filter(term=term, lesson_type=lesson_type, student=student, tutor=tutor).exists():
            raise ValidationError('A booking with the same details already exists.')

        return cleaned_data


class SessionForm(forms.ModelForm):
    """Form to create sessions"""
    class Meta:
        model = Session
        unique_together = ('booking', 'session_date', 'session_time')
        fields = ['booking', 'session_date', 'session_time', 'duration', 'venue', 'payment_status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['booking'].widget = forms.HiddenInput()
        booking = self.initial.get('booking', self.instance.booking if self.instance.pk else None)
        

    def clean(self):
        cleaned_data = super().clean()
        booking = cleaned_data.get('booking')
        duration = cleaned_data.get('duration')
        session_date = cleaned_data.get('session_date')
        session_time = cleaned_data.get('session_time')
        
        if booking and session_date and session_time:
            if Session.objects.filter(booking=booking, session_date=session_date, session_time=session_time).exists():
                raise forms.ValidationError(
                    {"__all__": "A session with this booking and date already exists."}
                )

        return cleaned_data
    

    def clean_session_date(self):
        session_date = self.cleaned_data.get('session_date')

        if session_date and session_date < datetime.now().date():
            raise forms.ValidationError("The session date cannot be in the past.")
        
        return session_date


class UpdateSessionForm(forms.ModelForm):
    """Form to update sessions"""
    class Meta:
        model = Session
        fields = ['session_date', 'session_time', 'duration', 'venue', 'payment_status']
    
    def clean(self):
        cleaned_data = super().clean()
        session_date = cleaned_data.get('session_date')
        session_time = cleaned_data.get('session_time')
        booking = cleaned_data.get('booking')

        if session_date and session_time:
            if Session.objects.filter(booking=booking, session_date=session_date, session_time=session_time).exists():
                raise forms.ValidationError("A session with the same booking, date, and time already exists.")
        if session_date and session_date < date.today():
            self.add_error('session_date', "Session date cannot be in the past.")
        
        return cleaned_data
