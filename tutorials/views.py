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
from .models import Booking, Session, User, Student, StudentRequest, Tutor, Subject
from .forms import BookingForm, SessionForm, UserForm, StudentForm,StudentRequestForm, TutorForm
from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from django.http import HttpResponseForbidden, HttpResponseRedirect,Http404



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
    redirect_when_logged_in_url = REDIRECT_URL_WHEN_LOGGED_IN = 'dashboard' 


    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or 'dashboard' 
        user = form.get_user()
        if user is not None:
            # check if user is an admin
            if user.user_type == 'admin':
                login(request, user)
                return redirect(self.next)
            else:
                messages.add_message(request, messages.ERROR, "Access denied: Only Admin users are allowed to log in.")
                return self.render()
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
    """Display the sign-up screen and handle sign-ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        """Handle valid form submission."""
        self.object = form.save()
        messages.success(self.request, "Registration successful! Please log in.")
        # redirect to login page after successful sign up
        return redirect('log_in')

    def get_success_url(self):
        """Override the default success URL."""
        return reverse('log_in')


def populate():
    """Used in user_list, tutor_list, and student_list to ensure they are populated."""
    users = User.objects.all()
    for user in users:
        if user.user_type == 'student' and not Student.objects.filter(username=user).exists():
            Student.objects.get_or_create(
                username=user, defaults={'name': user.full_name, 'email': user.email.lower()}
            )
        elif user.user_type == 'tutor' and not Tutor.objects.filter(username=user).exists():
            Tutor.objects.get_or_create(
                username=user, defaults={'name': user.full_name, 'email': user.email.lower()}
            )
 
"""User page"""           
@login_required
def users_list(request):
    """Display a list of all users with filtering, sorting, and searching options."""
    user_type_filter = request.GET.get('user_type')  
    order_by = request.GET.get('order_by')  
    search_query = request.GET.get('search', '')  

    users = User.objects.all()
    populate()
    # Apply filtering by user type
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)

    # Apply searching by name
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
        )

    # Apply ordering by name
    if order_by == 'asc':  # A-Z
        users = users.order_by('first_name', 'last_name')
    elif order_by == 'desc':  # Z-A
        users = users.order_by('-first_name', '-last_name') 
        
    
            
    return render(request, 'users/users_list.html', {
        'users': users,
        'user_type_filter': user_type_filter,
        'order_by': order_by,
        'search_query': search_query,
    })
@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'users/edit_users_type.html', {'form': form, 'user': user})

@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users_list')
    else:
        form = UserForm()
    return render(request, 'users/create_user.html', {'form': form})


"""Student page"""
@login_required
def students_list(request):
    """Display a list of all students with filtering, sorting, and searching options."""
    
    allocated = request.GET.get('allocated')  # Filter for allocation status
    payment = request.GET.get('payment')  # Filter for payment status
    order = request.GET.get('order')  # Order by name
    search_query = request.GET.get('search')  # Search by name

    # Start with all students
    students = Student.objects.all()
    populate()
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
    return render(request, 'students/students_list.html', context)

@login_required
def show_student(request, student_id):
    """Display further info on a student"""
    try:
        context = {'student': Student.objects.get(id=student_id)}
    except Student.DoesNotExist:
        raise Http404(f"Could not find a student with primary key {student_id}")
    else:
        return render(request, 'students/show_student.html', context)
    
@login_required
def update_student(request,student_id):
    """Update student info"""
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
                except Exception as e:
                    form.add_error(None, f"It was not possible to save this student to the database, {e}")
                else:
                    path = reverse('students_list')  # go to list of students
                    return HttpResponseRedirect(path)
        else:
            form = StudentForm(instance=student)
        return render(request,'students/update_student.html', {'form':form, 'student':student})

@login_required
def delete_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        if student.username != request.user:  # Ownership check
            return HttpResponseRedirect(reverse('students_list'))
    except Student.DoesNotExist:
        raise Http404(f"Could not find a student with primary key {student_id}")

    if request.method == "POST":
        student.delete()
        return HttpResponseRedirect(reverse('students_list'))
    else:
        context = f'Are you sure you want to delete the following student: "{student.name}".'
        return render(request, 'students/delete_student.html', {'context': context, 'student': student})


"""Student requests page"""
@login_required
def student_requests(request):
    """Display a list of all student requests with filtering, search, and sorting options."""
    # Get filter parameters from the query string
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    request_type_filter = request.GET.get('request_type', '')
    search_query = request.GET.get('search', '')  # For search bar
    order_by = request.GET.get('order_by', '')  # For sorting

    # Fetch filtered requests
    requests = StudentRequest.objects.all()

    if status_filter:
        requests = requests.filter(status=status_filter)
    if priority_filter:
        requests = requests.filter(priority=priority_filter)
    if request_type_filter:
        requests = requests.filter(request_type=request_type_filter)
    if search_query:
        requests = requests.filter(name__icontains=search_query)  # Case-insensitive search

    # Apply sorting
    if order_by == 'asc':
        requests = requests.order_by('name')
    elif order_by == 'desc':
        requests = requests.order_by('-name')

    # Pass filters and requests to the template
    context = {
        'requests': requests,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'request_type_filter': request_type_filter,
        'search_query': search_query,
        'order_by': order_by,
        'statuses': [choice[0] for choice in StudentRequest._meta.get_field('status').choices],
        'priorities': [choice[0] for choice in StudentRequest._meta.get_field('priority').choices],
        'request_types': [choice[0] for choice in StudentRequest._meta.get_field('request_type').choices],
    }
    return render(request, 'students_requests/student_requests.html', context)

@login_required
def show_request(request, request_id):
    """Display further information on a student request."""
    try:
        context = {'student_request': StudentRequest.objects.get(id=request_id)}
    except StudentRequest.DoesNotExist:
        raise Http404(f"Could not find a request with primary key {request_id}")
    else:
        return render(request, 'students_requests/show_request.html', context)

@login_required
def create_request(request):
    """Create a new student request and save it to the database."""
    if request.method == "POST":
        form = StudentRequestForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                form.add_error(None, "It was not possible to save this request to the database.")
            else:
                path = reverse('student_requests')
                return HttpResponseRedirect(path)
    else:
        form = StudentRequestForm()

    return render(request, 'students_requests/create_request.html', {'form': form})

@login_required
def update_request(request, request_id):
    """Update an existing student request in the database."""
    try:
        student_request = StudentRequest.objects.get(id=request_id)
    except StudentRequest.DoesNotExist:
        raise Http404(f"Could not find a request with primary key {request_id}")
    else:
        if request.method == "POST":
            form = StudentRequestForm(request.POST, instance=student_request)
            if form.is_valid():
                try:
                    form.save()  # Save the updated data to the database
                except Exception as e:
                    form.add_error(None, "It was not possible to save this request to the database.")
                else:
                    path = reverse('student_requests')  # Redirect to the list of requests
                    return HttpResponseRedirect(path)
        else:
            form = StudentRequestForm(instance=student_request)

        return render(request, 'students_requests/update_request.html', {'form': form, 'student_request': student_request})

@login_required
def delete_request(request, request_id):
    """Delete a student request from the database."""
    try:
        student_request = StudentRequest.objects.get(id=request_id)
    except StudentRequest.DoesNotExist:
        raise Http404(f"Could not find a request with primary key {request_id}")

    if request.method == "POST":
        # If the user confirmed deletion, delete the request and redirect
        student_request.delete()
        path = reverse('student_requests')  # Redirect to the list of requests
        return HttpResponseRedirect(path)
    else:
        # If request is GET, show confirmation page
        context = f'Are you sure you want to delete the following request: "{student_request}"?'
        return render(request, 'students_requests/delete_request.html', {'context': context, 'student_request': student_request})


"""Booking page"""
@login_required
def bookings_list(request):
    """Display a list of all bookings with filtering, ordering, and searching options."""
    term_filter = request.GET.get('term')  # Filter by term
    lesson_type_filter = request.GET.get('lesson_type')  # Filter by lesson type
    order_by = request.GET.get('order')  # Order by student or tutor name
    student_search = request.GET.get('student_search')  # Search for student name
    tutor_search = request.GET.get('tutor_search')  # Search for tutor name

    # Annotate full_name for students and tutors using Concat
    bookings = Booking.objects.annotate(
        student_name=F('student__name'),
        tutor_name=F('tutor__name')
    )


    # Filter by term
    if term_filter:
        bookings = bookings.filter(term=term_filter)

    # Filter by lesson type
    if lesson_type_filter:
        bookings = bookings.filter(lesson_type=lesson_type_filter)

    # Search for student name
    if student_search:
        bookings = bookings.filter(student_name__icontains=student_search)

    # Search for tutor name
    if tutor_search:
        bookings = bookings.filter(tutor_name__icontains=tutor_search)

    # Order by student or tutor name
    if order_by == 'student_asc':
        bookings = bookings.order_by('student_name')
    elif order_by == 'student_desc':
        bookings = bookings.order_by('-student_name')
    elif order_by == 'tutor_asc':
        bookings = bookings.order_by('tutor_name')
    elif order_by == 'tutor_desc':
        bookings = bookings.order_by('-tutor_name')

    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
        'term_choices': Booking.TERM_CHOICES,
        'lesson_type_choices': Booking.LESSON_TYPE_CHOICES,
        'term_filter': term_filter,
        'lesson_type_filter': lesson_type_filter,
        'order_by': order_by,
        'student_search': student_search,
        'tutor_search': tutor_search,
    })

# Create Booking
@login_required
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

@login_required
def booking_detail(request, pk):
    """Show details of a specific booking."""
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'bookings/booking_show.html', {'booking': booking})


@login_required
def booking_show(request, booking_id):
    """List all sessions for a specific booking with filtering and ordering."""
    booking = get_object_or_404(Booking, id=booking_id)
    sessions = booking.sessions.all()


    # Get filter values from request
    venue = request.GET.get('venue', None)
    payment_status = request.GET.get('payment', None)
    order = request.GET.get('order', None)
    
    print(f"Initial Sessions: {booking.sessions.all()}")
    print(f"Venue Filter: {venue}")
    print(f"Payment Status Filter: {payment_status}")

    # Apply filters
    if venue:
        sessions = sessions.filter(venue=venue)
    if payment_status:
        sessions = sessions.filter(payment_status=payment_status)

    # Apply ordering
    if order == 'closest':
        sessions = sessions.order_by('session_date')
    elif order == 'furthest':
        sessions = sessions.order_by('-session_date')
    
    print(f"Booking: {booking}")
    print(f"Filtered Sessions: {sessions}")
    
    # Calculate Total Amount
    for session in sessions:
        session.calculated_total_amount = session.total_amount

    return render(
        request,
        'bookings/booking_show.html',
        {
            'booking': booking,
            'sessions': sessions,
            'venue_choices': Session.VENUE_CHOICES,
            'payment_status_choices': Session.PAYMENT_STATUS_CHOICES,
        },
    )

"""Session page"""
@login_required
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

    return render(request, 'sessions/session_create.html', {'form': form, 'booking': booking})

@login_required
def session_show(request, pk):
    """Show details of a specific session."""
    session = get_object_or_404(Session, pk=pk)
    return render(request, 'sessions/session_show.html', {'session': session})

@login_required
def session_update(request, pk):
    """Update a specific session."""
    session = get_object_or_404(Session, pk=pk)  # Fetch the session or return 404

    if request.user != session.booking.student.username and not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)  # Bind data to the form
        if form.is_valid():
            form.save()  # Save the session
            return redirect('session_list', booking_id=session.booking.id)  # Redirect to booking details
    else:
        form = SessionForm(instance=session)  # Populate the form with session data

    return render(request, 'sessions/session_update.html', {'form': form, 'session': session})

@login_required
def session_delete(request, pk):
    """Delete a specific session."""
    session = get_object_or_404(Session, pk=pk)  # Fetch the session or return 404

    if request.method == 'POST':
        booking_id = session.booking.id  # Get the booking ID before deleting
        session.delete()  # Delete the session
        return redirect('session_list', booking_id=booking_id)  # Redirect to booking details

    return render(request, 'sessions/session_delete.html', {'session': session})


"""Tutor page"""
@login_required
def tutors_list(request):
    """Display a list of all tutors."""
    subjects = [
        'Python', 'Java', 'Javascript', 'React',
        'Ruby', 'Go', 'HTML/CSS', 'C', 'Scala'
    ]
    for subject in subjects:
        Subject.objects.get_or_create(name = subject)
        
    subject_filter = request.GET.get('subject')  #gets the subject filter
    order = request.GET.get('order')  #gets the order filter
    search_query = request.GET.get('search')  #gets the search query
    
    tutors = Tutor.objects.all()
    populate()

    #filter tutors by subject if provided
    if subject_filter:
        tutors = tutors.filter(subjects__id=subject_filter) #ManyToManyField filter

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
    subject_choices = [(subject.id, subject.name) for subject in all_subjects]
    return render(request, 'tutors/tutors_list.html', {
        'tutors': tutors,
        'subject_choices': subject_choices,
        'current_order': order,  
        'search_query': search_query,  
        'current_subject': subject_filter,
    })

@login_required
def show_tutor(request, tutor_id):
    """Display further info on a tutor"""

    try:
        tutor = Tutor.objects.get(id=tutor_id)
    except Tutor.DoesNotExist:
        raise Http404(f"Could not find a tutor with primary key {tutor_id}")
    
    
    subjects = tutor.subjects.all()

    return render (request, 'tutors/show_tutor.html', {
        'tutor': tutor,
        'subjects': subjects
    })

@login_required
def update_tutor(request,tutor_id):
    tutor = get_object_or_404(Tutor, id=tutor_id)
    if request.method == 'POST':
        form = TutorForm(request.POST, instance=tutor) 
        if form.is_valid(): 
            form.save()  
            return redirect('tutors_list')  
    else:
        form = TutorForm(instance=tutor)  
    return render(request, 'tutors/update_tutor.html', {'form': form, 'tutor': tutor})

@login_required
def delete_tutor(request,tutor_id):
    try:
        tutor = Tutor.objects.get(id=tutor_id)
    except Tutor.DoesNotExist:
        raise Http404(f"Could not find a tutor with primary key {tutor_id}")

    if request.method == "POST":
        tutor.delete()
        path = reverse('tutors_list')  
        return HttpResponseRedirect(path)
    else:
        context = f'Are you sure you want to delete the following tutor: "{tutor.name}".'
        return render(request,'tutors/delete_tutor.html', {'context': context,'tutor':tutor})
    
    