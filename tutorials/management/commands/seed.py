from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, Student, Tutor, Booking, Session #
import pytz
from faker import Faker
from random import randint, random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

 ##
 
user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe','Type':'Admin'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe','Type':'Tutor','Subject':''},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson','Type':'Student','Allocated':False,'Payment':'Pending'}, # Or [(PENDING, 'Pending'),(SUCCESSFUL, 'Successful')]
    
    #Extra predefined users
    {'username': '@Jamesdan', 'email': 'james.dan@example.org', 'first_name': 'James', 'last_name': 'Dan','Type':'Admin'},
    {'username': '@Bobmark', 'email': 'bob.mark@example.org', 'first_name': 'Bob', 'last_name': 'Mark','Type':'Tutor','Subject':''},
    {'username': '@Saralee', 'email': 'sara.lee@example.org', 'first_name': 'Sara', 'last_name': 'Lee','Type':'Student','Allocated':False,'Payment':'Pending'}, # Or [(PENDING, 'Pending'),(SUCCESSFUL, 'Successful')]
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    #BOOKING_COUNT = 200?
    #SESSION_COUNT = 100?
    #?TUTOR_COUNT = 75 
    #?STUDENT_COUNT = 210
    #?ADMIN_COUNT = 15
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options): #make sure it's correct
        self.create_users()
        self.create_bookings()
        self.create_sessions()
        self.users = User.objects.all()
        self.booking = Booking.objects.all()
        self.sessions = Session.objects.all()


    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()
    
    #####
    def create_bookings(self):
        self.generate_random_bookings()
        
    def create_sessions(self):      
        self.generate_random_sessions()
    #####

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)


    def generate_random_users(self): ##
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete. ")
        
    #
    def generate_random_bookings(self): ##
        booking_count = Booking.objects.count()
        while  booking_count < self.BOOKING_COUNT:
            print(f"Seeding booking {booking_count}/{self.BOOKING_COUNT}", end='\r')
            self.generate_booking()
            booking_count = Booking.objects.count()
        print("Booking seeding complete. ")
        
    def generate_random_sessions(self): ##
        session_count = Session.objects.count()
        while  session_count < self.SESSION_COUNT:
            print(f"Seeding session {session_count}/{self.SESSION_COUNT}", end='\r')
            self.generate_session()
            session_count = Session.objects.count()
        print("Session seeding complete. ") 

    #   
         
    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        user_type = self.generate_random_user_type()
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'type': user_type})
       
    #
    
    def generate_booking(self):
        print("Creating Bookings")
        terms = ['Term 1', 'Term 2', 'Term 3']
        students = Student.objects.all()
        tutors = Tutor.objects.all()

        if not students.exists() or not tutors.exists():
            print("Insufficient students or tutors to create bookings.")
            return

        for _ in range(self.BOOKING_COUNT):
            student = random.choice(students)
            tutor = random.choice(tutors)
            term = random.choice(terms)
            try:
                booking = Booking.objects.create(
                    term=term,
                    student=student,
                    tutor=tutor
                )
            except Exception as e:
                print(f"Error creating booking: {e}")
                continue
        print(f"Created {Booking.objects.count()} bookings.")

        
        
    def generate_session(self):
        bookings = Booking.objects.all()
        lesson_types = ['Fortnight', 'Weekly', 'Bi-Weekly']
        venues = ['Bush House', 'Waterloo Campus']

        if not bookings.exists():
            print("No bookings available to create sessions.")
            return

        for _ in range(self.SESSION_COUNT):
            booking = random.choice(bookings)
            session_date = self.faker.date_between(start_date="today", end_date="+30d")#
            session_time = self.faker.time_object() #8am - 6pm
            duration = timedelta(hours=random.randint(1, 4)) # 1 - 4 
            lesson_type = random.choice(lesson_types) # add to bookings instead of session
            venue = random.choice(venues)
            payment_status = random.choice(['Pending', 'Successful'])

            try:
                session = Session.objects.create(
                    booking=booking,
                    session_date=session_date,
                    session_time=session_time,
                    duration=duration,
                    lesson_type=lesson_type,
                    venue=venue,
                    payment_status=payment_status,
                )
            except Exception as e:
                print(f"Error creating session: {e}")
                continue
        print(f"Created {Session.objects.count()} sessions.")

             
       
    #  
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except Exception as e: #not sure tbh
            print(f"Error creating user {data ['username']}:{e}") #pass

    def create_user(self, data):
        base_data = {
            'username' : data['username'],
            'email' : data['email'],
            'password' : Command.DEFAULT_PASSWORD,
            'first_name' : data['first_name'],
            'last_name' : data['last_name'],
            'type': data['type']
        }
        
        if data['type'] == 'Student':
            student = Student.objects.create_user(
                **base_data 
            )
            return student
        
        if data['type'] == 'Tutor':
            tutor = Tutor.objects.create_user(
                **base_data 
            )
            return tutor
        
        elif data['type'] == 'Admin':
            user = User.objects.create_user(
                **base_data # what can the admin access
            )
            return user
        
             

def create_username(first_name, last_name):
    base_username = '@' + first_name.strip().lower() + last_name.strip().lower()
    username = base_username
    counter = 1

    # Check existing usernames efficiently
    existing_usernames = User.objects.filter(username__startswith=base_username).values_list('username', flat=True)

    while username in existing_usernames:
        username = f"{base_username}{counter}"
        counter += 1

    return username


def create_email(first_name, last_name):
    base_email = f"{first_name.strip().lower()}.{last_name.strip().lower()}@example.org"
    email = base_email
    counter = 1

    # Check existing emails efficiently
    existing_emails = User.objects.filter(email__startswith=base_email).values_list('email', flat=True)

    while email in existing_emails:
        email = f"{first_name.strip().lower()}.{last_name.strip().lower()}{counter}@example.org"
        counter += 1

    # Validate the constructed email
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError(f"Generated email '{email}' is invalid.")

    return email


def generate_random_user_type():
    user_types = ['Student', 'Tutor', 'Admin']
    weights = [70, 25, 5]  # Corresponding to 70% students, 25% tutors, 5% admins
    return random.choices(user_types, weights=weights, k=1)[0]
