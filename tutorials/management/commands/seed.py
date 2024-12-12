from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from tutorials import models
from tutorials.models import User, Student, Tutor, Booking, Session, StudentRequest, Subject #
import pytz
from faker import Faker
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

 ##
 
user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe','user_type':'Admin'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe','user_type':'Tutor'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson','user_type':'Student',}, 
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    BOOKING_COUNT = 200 
    SESSION_COUNT = 100
    STUDENT_REQUEST_COUNT = 50

    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')
        #Tala says add the functions in handle here
        

    def handle(self, *args, **options): 
        self.create_users() #ERROR
        self.generate_random_bookings() #ERROR
        self.generate_random_sessions()
        self.users = User.objects.all()
        self.booking = Booking.objects.all()
        self.sessions = Session.objects.all()


    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()    #ERROR
    

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)


    def generate_random_users(self): 
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()    #ERROR
            user_count = User.objects.count()
        print("Users seeding complete. ")
        
    #
    def generate_random_bookings(self): ##
        booking_count = Booking.objects.count()
        while  booking_count < self.BOOKING_COUNT: 
            print(f"Seeding booking {booking_count}/{self.BOOKING_COUNT}", end='\r')
            self.generate_booking() #ERROR
            booking_count = Booking.objects.count()
        print("Bookings seeding complete. ")
        
    def generate_random_sessions(self): ##
        session_count = Session.objects.count()
        while  session_count < self.SESSION_COUNT:
            print(f"Seeding session {session_count}/{self.SESSION_COUNT}", end='\r')
            self.generate_session()
            session_count = Session.objects.count()
        print("Sessions seeding complete. ") 
        
    def generate_random_studentRequests(self): ##
        student_request_count = StudentRequest.objects.count()
        while  student_request_count < self.STUDENT_REQUEST_COUNT:
            print(f"Seeding student request {student_request_count}/{self.STUDENT_REQUEST_COUNT}", end='\r')
            self.generate_student_request()
            student_request_count = StudentRequest.objects.count()
        print("Student requests seeding complete. ") 

    #   
         
    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self.create_email(first_name, last_name)
        username = self.create_username(first_name, last_name)
        user_type = self.generate_random_user_type()

        try:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "password": self.DEFAULT_PASSWORD,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            if not created:
                print(f"User {username} already exists.")
        except Exception as e:
            print(f"Error creating user {username}: {e}")

    #

    def generate_booking(self):
        terms = ['Term 1', 'Term 2', 'Term 3']
        lesson_types = ['Fortnight', 'Weekly', 'Bi-Weekly']
        students = Student.objects.all()
        tutors = Tutor.objects.all()

        if not students.exists() or not tutors.exists():
            print("No students or tutors available to create bookings.")
            return

        for _ in range(self.BOOKING_COUNT):
            student = random.choice(students)
            tutor = random.choice(tutors)
            term = random.choice(terms)
            lesson_type = random.choice(lesson_types)

            # Check for duplicates
            if Booking.objects.filter(term=term, lesson_type=lesson_type, student=student, tutor=tutor).exists():
                print(f"Skipping duplicate booking for {student} and {tutor}")
                continue
            else:
                print(f"Created booking for {student} with {tutor} in {term}.")

            try:
                Booking.objects.create(term=term, lesson_type=lesson_type, student=student, tutor=tutor)
            except Exception as e:
                print(f"Error creating booking: {e}")


        
    def generate_session(self):     #ERROR i think
        print('Creating sessions.. ')
        bookings = Booking.objects.all()
        #session times
        venues = ['Bush House', 'Waterloo Campus']
        
        if not bookings.exists():
            print("No bookings available to create sessions.")
            return

        for _ in range(self.SESSION_COUNT):
            booking = random.choice(bookings)
            session_date = self.faker.date_between(start_date="today", end_date="+90d")
            session_time = self.faker.time_object() #from 9am to 6pm
            duration = timedelta(hours=random.randint(1, 4)) # 1 - 3 hours      #check this
            venue = random.choice(venues)
            payment_status = random.choice(['Pending', 'Successful'])

            try:
                Session.objects.create(
                    booking=booking,
                    session_date=session_date,
                    session_time=session_time,
                    duration=duration,
                    venue=venue,
                    payment_status=payment_status,
                )
            except Exception as e:
                print(f"Error creating session: {e}")
                continue
        print(f"Created {Session.objects.count()} sessions.")
       
    def generate_student_request(self):                 #Needs checking if it works or not
        # 1. Ensure that at least 1 student exists
        
        for _ in range(self.STUDENT_REQUEST_COUNT):
            student = random.choice(Student.objects.all())
            name = student.name
            username = student.username
            request_type = random.choice(['Profile Update', 'Password Reset', 'Course Enrollment', 'Tutor Assignment', 'Session Scheduling', 'Payment Issue','Technical Support', 'Feedback/Complaint', 'Custom Request'])
            description=self.faker.text(max_nb_chars=200)            
            status= random.choice(['Pending', 'In Progress', 'Resolved'])
            priority=random.choice(['Low','Medium','High'])
            created_at= faker.date_between(start_date='-30d', end_date='today')
            try:
                StudentRequest.objects.create(
                    student=student,
                    username=username,
                    request_type=request_type,
                    description=description,
                    status=status,
                    priority=priority,
                    created_at=created_at
                )
                
            except Exception as e:
                print(f"Error creating student request: {e}")
                continue
                
        return
    #  
       
    def try_create_user(self, data):
        if User.objects.filter(email=data['email']).exists():
            print(f"Skipping user {data['username']} as email already exists.")
            return
        try:
            self.create_user(data)
        except Exception as e: #not sure tbh
            print(f"Error creating user {data ['username']}: {e}") #it used to be pass

    def create_user(self, data):
        base_data = {
            'username': data['username'],
            'email': data['email'],
            'password': self.DEFAULT_PASSWORD,
            'first_name': data['first_name'],       #
            'last_name': data['last_name'],
        }
        
        # Create User instance first
        user = User.objects.create_user(**base_data, user_type=data['user_type'].lower())

        if data['user_type'] == 'Student':
            student = Student.objects.create(
                name=f"{data['first_name']} {data['last_name']}",
                username=user,
                email=data['email'],
                allocated=random.choice([True,False]), 
                payment=random.choice(['Successful', 'Pending'])  
            )
            return student
        elif data['user_type'] == 'Tutor':
            tutor = Tutor.objects.create(
                name=f"{data['first_name']} {data['last_name']}",
                username=user,
                email=data['email'],
                subjects= Subject.objects.create(name="Python"),        #Check This
                rate=random.choice([10.0,20.0,30.0,40.0,50.0])  
            )
            return tutor
        elif data['user_type'] == 'Admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
            return user
        
    

    
    def create_username(self,first_name, last_name):
        base_username = '@' + first_name.strip().lower() + last_name.strip().lower()
        username = base_username
        counter = 1

        # Check existing usernames efficiently
        existing_usernames = User.objects.filter(username__startswith=base_username).values_list('username', flat=True)

        while username in existing_usernames:
            username = f"{base_username}{counter}"
            counter += 1

        return username



    def create_email(self, first_name, last_name):
        base_email = f"{first_name.strip().lower()}.{last_name.strip().lower()}@example.org"
        email = base_email
        counter = 1

        existing_emails = User.objects.filter(email__startswith=base_email).values_list('email', flat=True)

        while User.objects.filter(email=email).exists():  # Check for duplicates
            email = f"{first_name.strip().lower()}.{last_name.strip().lower()}{counter}@example.org"
            counter += 1

        return email

    
    def generate_random_user_type(self):    #DOUBLE CHECK PLZ!
        user_types = ['Student', 'Tutor']  
        weights = [70, 30]  # Corresponding to 70% students, 30% tutors
        return random.choices(user_types, weights=weights, k=1)[0]

