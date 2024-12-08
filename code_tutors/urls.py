"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views
from tutorials.views import list_tutors, update_tutor, delete_tutor, show_tutor

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    # Inside welcome page (root URL)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),

    #tutor add-ons
    path('tutors/',views.list_tutors, name='tutors'),
    path('tutors/<int:tutor_id>/',views.show_tutor, name='show_tutor'),
    path('tutors/<int:tutor_id>/edit/', views.update_tutor, name='update_tutor'),
    path('tutors/<int:tutor_id>/delete/', views.delete_tutor, name='delete_tutor'),

    #Students add-ons
    path('students/',views.students_list, name='students'),
    path('students/<int:student_id>/',views.show_student, name='show_student'),
    path('update_student/<int:student_id>/', views.update_student, name='update_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),

    #Student Requests add-ons
    path('requests/', views.student_requests, name='student_requests'),
    path('requests/<int:request_id>/', views.show_request, name='show_request'),
    path('create_request/', views.create_request, name='create_request'),
    path('update_request/<int:request_id>/', views.update_request, name='update_request'),
    path('delete_request/<int:request_id>/', views.delete_request, name='delete_request'),

    #Users add-ons
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_users_type'),
    #path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    #Booking add-ons
    # List all bookings (Page 1)
    path('bookings/', views.bookings_list, name='booking_list'),
    
    # Update a specific booking (Page 3)
    path('bookings/update/<int:pk>/', views.booking_update, name='booking_update'),
    
    # Confirm and delete a specific booking (Page 4)
    path('bookings/delete/<int:pk>/', views.booking_delete, name='booking_delete'),

    path('bookings/create/', views.booking_create, name='booking_create'),  # Create Booking
    path('bookings/show/<int:pk>/', views.booking_detail, name='booking_detail'),  # Booking details
    path('bookings/<int:booking_id>/sessions/', views.booking_show, name='session_list'),
    path('sessions/<int:pk>/', views.session_show, name='session_show'),
    path('sessions/update/<int:pk>/', views.SessionUpdateView.as_view(), name='session_update'),
    path('sessions/delete/<int:pk>/', views.SessionDeleteView.as_view(), name='session_delete'),


    path('bookings/<int:booking_id>/sessions/create/', views.session_create, name='session_create'),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)