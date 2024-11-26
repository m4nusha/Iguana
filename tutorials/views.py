from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited

from .models import Tutor
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
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
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
    

########## my additions ##########

def list_tutors(request):
    """Display a list of all tutors."""
    tutors = Tutor.objects.all()
    return render(request, 'list_tutors.html', {'tutors': tutors})


def show_tutor(request, tutor_id):
    """Display further info on a student"""
    try:
        context = {'tutor': Tutor.objects.get(id=tutor_id)}
    except Tutor.DoesNotExist:
        raise Http404(f"Could not find a tutor with primary key {tutor_id}")
    else:
        return render(request, 'show_tutor.html', context)


def create_tutor(request):
    """Create a new tutor to the database"""
    #Check first if it's a post request
    if request.method == "POST":
        form = TutorForm(request.POST)
        #Then check if the data entered is valid
        if form.is_valid():
            try:
                form.save()
            except:
                form.add_error(None, "It was not possible to save this tutor to the database,")
            else:
                path = reverse('tutors')     #Go to  list of tutors
                return HttpResponseRedirect(path)
    else:
        form = TutorForm()
    return render(request, 'create_tutor.html', {'form':form})


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
