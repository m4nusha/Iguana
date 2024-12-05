from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from .models import Booking, Session
from .forms import BookingForm, SessionForm
from django.shortcuts import get_object_or_404
from django.db.models import Value, F, Func, CharField, Q


from .models import Student
from .forms import StudentForm
from django.http import HttpResponse, HttpResponseRedirect,Http404

from .models import Tutor, Subject
from .forms import TutorForm
from django.http import HttpResponse, HttpResponseRedirect, Http404
from tutorials import views


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = REDIRECT_URL_WHEN_LOGGED_IN = 'dashboard' #made changes here


    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or 'booking_list' #Made changes in here!!!
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


def students(request):
    """Display a list of all students with filtering, sorting, and searching options."""
    # Get filter and search parameters from the request
    allocated = request.GET.get('allocated')  # Filter for allocation status
    payment = request.GET.get('payment')  # Filter for payment status
    order = request.GET.get('order')  # Order by name
    search_query = request.GET.get('search')  # Search by name

    # Start with all students
    students = Student.objects.all()

    # Apply filtering by allocated
    if allocated == 'true':
        students = students.filter(allocated=True)
    elif allocated == 'false':
        students = students.filter(allocated=False)

    # Apply filtering by payment
    if payment:
        students = students.filter(payment=payment)

    # Apply searching by name
    if search_query:
        students = students.filter(name__icontains=search_query)

    # Apply sorting by name
    if order == 'asc':  # A-Z
        students = students.order_by('name')
    elif order == 'desc':  # Z-A
        students = students.order_by('-name')

    context = {
        'students': students,
        'current_allocated': allocated,
        'current_payment': payment,
        'current_order': order,
        'search_query': search_query,
        'payment_choices': Student.PAYMENT_CHOICES,  # Pass payment choices to the template
    }
    return render(request, 'students.html', context)

def show_student(request, student_id):
    """Display further info on a student"""
    try:
        context = {'student': Student.objects.get(id=student_id)}
    except Student.DoesNotExist:
        raise Http404(f"Could not find a student with primary key {student_id}")
    else:
        return render(request, 'show_student.html', context)

def create_student(request):
    """Create a new student to the database"""
    #check first if it's a post request
    if request.method == "POST":
        form = StudentForm(request.POST)
        #then check if the data entered is valid
        if form.is_valid():
            try:
                form.save()
            except:
                form.add_error(None, "It was not possible to save this student to the database,")
            else:
                path = reverse('students')     #go to  list of students
                return HttpResponseRedirect(path)
    else:
        form = StudentForm()
    return render(request, 'create_student.html', {'form':form})


def update_student(request,student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        raise Http404(f"Could not find a student with primary key {student_id}")
    else:
        if request.method == "POST":
            form = StudentForm(request.POST, instance=student)
            if form.is_valid():
                try:
                    form.save()
                except:
                    form.add_error(None, "It was not possible to save this student to the database,")
                else:
                    path = reverse('students')  # go to list of students
                    return HttpResponseRedirect(path)
        else:
            form = StudentForm(instance=student)
        return render(request,'update_student.html', {'form':form, 'student':student})


def delete_student(request,student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        raise Http404(f"Could not find a student with primary key {student_id}")

    if request.method == "POST":
            # If the user confirmed deletion, delete the student and redirect
        student.delete()
        path = reverse('students')  # go to list of students
        return HttpResponseRedirect(path)
    else:
            # If request is GET, show confirmation page
        context = f'Are you sure you want to delete the following student: "{student.name}".'
        return render(request,'delete_student.html', {'context': context,'student':student})
    
@login_required

def bookings_list(request):
    """Display a list of all bookings with filtering, ordering, and searching options."""
    term_filter = request.GET.get('term')  # Filter by term
    order_by = request.GET.get('order')  # Order by student or tutor name
    student_search = request.GET.get('student_search')  # Search for student name
    tutor_search = request.GET.get('tutor_search')  # Search for tutor name

    # Annotate full_name for students and tutors
    bookings = Booking.objects.annotate(
        student_full_name=Func(
            F('student__first_name'),
            Value(' '),
            F('student__last_name'),
            function='CONCAT',
            output_field=CharField()
        ),
        tutor_full_name=Func(
            F('tutor__first_name'),
            Value(' '),
            F('tutor__last_name'),
            function='CONCAT',
            output_field=CharField()
        )
    )

    # Filter by term
    if term_filter:
        bookings = bookings.filter(term=term_filter)

    # Search for student name
    if student_search:
        bookings = bookings.filter(student_full_name__icontains=student_search)

    # Search for tutor name
    if tutor_search:
        bookings = bookings.filter(tutor_full_name__icontains=tutor_search)

    # Order by student or tutor name
    if order_by == 'student_asc':
        bookings = bookings.order_by('student_full_name')
    elif order_by == 'student_desc':
        bookings = bookings.order_by('-student_full_name')
    elif order_by == 'tutor_asc':
        bookings = bookings.order_by('tutor_full_name')
    elif order_by == 'tutor_desc':
        bookings = bookings.order_by('-tutor_full_name')

    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
        'term_choices': Booking.TERM_CHOICES,
        'term_filter': term_filter,
        'order_by': order_by,
        'student_search': student_search,
        'tutor_search': tutor_search,
    })


# Create Booking
def booking_create(request):
    """Handle creation of a new booking."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'bookings/booking_create.html', {'form': form})

@login_required
def booking_update(request, pk):
    """Update a specific booking (Page 3)."""
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'bookings/booking_update.html', {'form': form})

@login_required
def booking_delete(request, pk):
    """Display confirmation page and delete a booking (Page 4)."""
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        return redirect('booking_list')
    return render(request, 'bookings/booking_delete.html', {'booking': booking})
#for tests only
def welcome(request):
    """Render the inside welcome page."""
    return render(request, 'welcome.html')

def booking_detail(request, pk):
    """Show details of a specific booking."""
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'bookings/booking_show.html', {'booking': booking})

from django.db.models import Q

def booking_show(request, booking_id):
    """List all sessions for a specific booking with filtering and ordering."""
    booking = get_object_or_404(Booking, id=booking_id)
    sessions = booking.sessions.all()

    # Get filter values from request
    lesson_type = request.GET.get('type', None)
    venue = request.GET.get('venue', None)
    payment_status = request.GET.get('payment', None)
    order = request.GET.get('order', None)

    # Apply filters
    if lesson_type:
        sessions = sessions.filter(lesson_type=lesson_type)
    if venue:
        sessions = sessions.filter(venue=venue)
    if payment_status:
        sessions = sessions.filter(payment_status=payment_status)

    # Apply ordering
    if order == 'closest':
        sessions = sessions.order_by('session_date')
    elif order == 'furthest':
        sessions = sessions.order_by('-session_date')

    return render(
        request,
        'bookings/booking_show.html',
        {
            'booking': booking,
            'sessions': sessions,
            'lesson_type_choices': Session.LESSON_TYPE_CHOICES,
            'venue_choices': Session.VENUE_CHOICES,
            'payment_status_choices': Session.PAYMENT_STATUS_CHOICES,
        },
    )


def session_create(request, booking_id):
    """Create a new session for a specific booking."""
    booking = get_object_or_404(Booking, id=booking_id)  # Get the booking instance
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            new_session = form.save(commit=False)
            new_session.booking = booking  # Ensure booking is set
            new_session.save()
            return redirect('session_list', booking_id=booking.id)
    else:
        # Prepopulate the booking field
        form = SessionForm(initial={'booking': booking})

    return render(request, 'bookings/sessions/session_create.html', {'form': form, 'booking': booking})

def session_show(request, pk):
    """Show details of a specific session."""
    session = get_object_or_404(Session, pk=pk)
    return render(request, 'bookings/sessions/session_show.html', {'session': session})

class SessionUpdateView(UpdateView):
    """Update a specific session."""
    model = Session
    fields = ['session_date', 'session_time', 'duration', 'lesson_type', 'venue', 'amount', 'payment_status']
    template_name = 'bookings/sessions/session_update.html'

    def get_success_url(self):
        # Use the booking ID of the related session
        return reverse_lazy('session_list', kwargs={'booking_id': self.object.booking.id})


class SessionDeleteView(DeleteView):
    """Delete a specific session."""
    model = Session
    template_name = 'bookings/sessions/session_delete.html'

    def get_success_url(self):
        # Use the booking ID of the related session
        return reverse_lazy('session_list', kwargs={'booking_id': self.object.booking.id})


########## my additions ##########

from .models import Tutor

def list_tutors(request):
    """Display a list of all tutors."""
    #!!!!!!
    subject_filter = request.GET.get('subject')  # Get the subject filter
    order = request.GET.get('order')  # Get the order filter
    search_query = request.GET.get('search')  # Get the search query
    
    tutors = Tutor.objects.all()

    #!!!!!
    # Filter tutors by subject if provided
    #if subject:
        #tutors = Tutor.objects.filter(subject=subject)
    #else:
        #tutors = Tutor.objects.all()

    #filter tutors by subject if provided
    if subject_filter:
        tutors = tutors.filter(subjects__name=subject_filter) #ManyToManyField filter

    #filter tutors by name if search query is provided
    if search_query:
        tutors = tutors.filter(name__icontains=search_query)

    #order tutors by name if ordering is specified
    if order == 'asc':  # A-Z
        tutors = tutors.order_by('name')
    elif order == 'desc':  # Z-A
        tutors = tutors.order_by('-name')

    #get all subjects for the filter dropdown
    all_subjects = Subject.objects.all()

    return render(request, 'list_tutors.html', {
        'tutors': tutors,
        'subject_choices': all_subjects,
        'current_order': order,  #pass current order for UI feedback
        'search_query': search_query,  #pass search query for UI feedback
        'current_subject': subject_filter, #pass the selected subject for UI feedback
    })


def show_tutor(request, tutor_id):
    """Display further info on a tutor"""

    # try:
    #     context = {'tutor': Tutor.objects.get(id=tutor_id)}
    # except Tutor.DoesNotExist:
    #     raise Http404(f"Could not find a tutor with primary key {tutor_id}")
    # else:
    #     return render(request, 'show_tutor.html', context)

    try:
        tutor = Tutor.objects.get(id=tutor_id)
    except Tutor.DoesNotExist:
        raise Http404(f"Could not find a tutor with primary key {tutor_id}")
    
    #pass tutor's subjects to the template
    subjects = tutor.subjects.all()

    return render (request, 'show_tutor.html', {
        'tutor': tutor,
        'subjects': subjects
    })


def update_tutor(request,tutor_id):
    try:
        tutor = Tutor.objects.get(id=tutor_id)
    except Tutor.DoesNotExist:
        raise Http404(f"Could not find a tutor with primary key {tutor_id}")
    else:
        if request.method == "POST":
            form = TutorForm(request.POST, instance=tutor)
            if form.is_valid():
                try:
                    form.save()
                except:
                    form.add_error(None, "It was not possible to save this tutor to the database,")
                else:
                    path = reverse('tutors')  # go to list of tutors
                    return HttpResponseRedirect(path)
        else:
            form = TutorForm(instance=tutor)
        return render(request,'update_tutor.html', {'form':form, 'tutor':tutor})


def delete_tutor(request,tutor_id):
    try:
        tutor = Tutor.objects.get(id=tutor_id)
    except Tutor.DoesNotExist:
        raise Http404(f"Could not find a tutor with primary key {tutor_id}")

    if request.method == "POST":
            # If the user confirmed deletion, delete the tutor and redirect
        tutor.delete()
        path = reverse('tutors')  # go to list of tutors
        return HttpResponseRedirect(path)
    else:
            # If request is GET, show confirmation page
        context = f'Are you sure you want to delete the following tutor: "{tutor.name}".'
        return render(request,'delete_tutor.html', {'context': context,'tutor':tutor})