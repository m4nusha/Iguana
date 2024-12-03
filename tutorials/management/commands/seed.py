from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, Student, Tutor, Booking, Session #
import pytz
from faker import Faker
from random import randint, random

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


"""""
booking_fixtures = [
    { Term : ,  student : , tutor :}
    { Term : ,  student : , tutor :}
    { Term : ,  student : , tutor :}
    ]
"""

"""
session_fixtures = [
    {'booking': , 'session_date': , 'session_time': , 'duration': , 'lesson_type': , 'venue': , 'payment_status': }
    {'booking': , 'session_date': , 'session_time': , 'duration': , 'lesson_type': , 'venue': , 'payment_status': }
    {'booking': , 'session_date': , 'session_time': , 'duration': , 'lesson_type': , 'venue': , 'payment_status': }
]
"""

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    #BOOKING_COUNT = 200?
    #SESSION_COUNT = 100?
    
    # Might delete them
    #?TUTOR_COUNT = 75 
    #?STUDENT_COUNT = 210
    #?ADMIN_COUNT = 15
    
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.create_bookings()#
        self.create_sessions()#
        self.users = User.objects.all()
        self.booking = Booking.objects.all()#
        self.sessions = Session.objects.all()#


    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()
    
    #####
    def create_bookings(self):
        self.generate_booking_fixtures()
        self.generate_random_bookings()
        
    def create_sessions(self):
        self.generate_session_fixtures()
        self.generate_random_sessions()
    #####

        
    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)
            
    
    def generate_booking_fixtures(self):
        for data in booking_fixtures:
            self.try_create_booking(data)
            
    def generate_session_fixtures(self):
        for data in session_fixtures:
            self.try_create_session(data)


    def generate_random_users(self): ##
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete. ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        user_type = self.random_user_type()
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'type': user_type})
       
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
                **base_data #
            )
            return student
        
        if data['type'] == 'Tutor':
            tutor = Tutor.objects.create_user(
                **base_data #
            )
            return tutor
        
        elif data['type'] == 'Admin':
            user = User.objects.create_user(
                **base_data #
            )
            return user
        else:   
            user = User.objects.create_user(**base_data) # Might delete this else
            return user
             

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()
    #check if username already exists in the database

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'
    #check if email already exists in the database


def random_user_type(): #needs improvement 
    return random.choices(
        ['Student', 'Tutor', 'Admin'],
        weights = [0.7,0.25, 0.05] #70% students 25% tutors 5% admins
        k=1
    )[0]

def create_sessions(): # Session Date, session time, duration, venue, payment staus, tutor rates
    return

def create_bookings(): # Term,      lesson type,         student, tutor
    return

