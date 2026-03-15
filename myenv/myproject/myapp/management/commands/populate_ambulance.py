from django.core.management.base import BaseCommand
from myapp.models import Staff, Ambulance, AmbulanceBooking
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with Ambulance test data'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        self.stdout.write('Populating Ambulance Data...')

        # 1. Create Drivers
        drivers = []
        for i in range(1, 6):
            username = f'driver{i}'
            email = f'driver{i}@example.com'
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(username=username, password='password123', email=email)
                user.user_type = 'staff'
                user.save()

            # Check if Staff profile exists
            staff, created = Staff.objects.get_or_create(
                user=user,
                defaults={
                    'name': f'Driver {i}',
                    'role': 'Driver',
                    'phone': f'987654320{i}',
                    'email': email,
                    # staff_id is auto-generated
                }
            )
            
            if not created:
                # Update role if needed
                if staff.role != 'Driver':
                    staff.role = 'Driver'
                    staff.save()
            
            drivers.append(staff)
            self.stdout.write(f'Created/Updated Driver: {staff.name}')

        # 2. Create Ambulances
        vehicle_types = ['Basic', 'ICU', 'Oxygen']
        
        ambulances = []
        for i in range(1, 11):
            v_num = f'AMB-{100+i}'
            driver = None
            status = 'Available'

            # Assign some as busy
            if i % 3 == 0:
                status = 'Busy'
                driver = random.choice(drivers) if drivers else None
            elif i % 5 == 0:
                status = 'Maintenance'
            
            # Ensure unique driver assignment (simplified for test data)
            if driver and Ambulance.objects.filter(driver=driver).exists():
                 driver = None 
                 status = 'Available' # Fallback

            amb, created = Ambulance.objects.get_or_create(
                vehicle_number=v_num,
                defaults={
                    'vehicle_type': random.choice(vehicle_types),
                    'status': status,
                    'driver': driver
                }
            )
            ambulances.append(amb)
            self.stdout.write(f'Created Ambulance: {amb.vehicle_number}')

        # 3. Create Bookings
        locations = ['City Center', 'North Ave', 'South Park', 'West End', 'East Side']
        
        for i in range(20):
            status = random.choice(['Pending', 'Confirmed', 'Completed', 'Cancelled'])
            
            # Request date
            days_ago = random.randint(0, 10)
            req_date = timezone.now() - timedelta(days=days_ago)
            
            booking = AmbulanceBooking(
                patient_name=f'Patient {i}',
                contact_phone=f'555-010{i}',
                from_location=random.choice(locations),
                to_location='General Hospital',
                request_date=req_date,
                status=status
            )
            
            if status in ['Confirmed', 'Completed']:
                # Find a suitable ambulance
                # For test data, just pick one, doesn't matter if it matches the current status perfectly
                booking.ambulance = random.choice(ambulances)
                booking.driver = booking.ambulance.driver
                
                # If ambulance has no driver, pick a random driver
                if not booking.driver and drivers:
                    booking.driver = random.choice(drivers)

                booking.distance_km = random.uniform(5.0, 50.0)
                booking.total_amount = 500 + (booking.distance_km * 50)
                
                if status == 'Completed':
                    booking.completion_date = req_date + timedelta(hours=1)
            
            booking.save()
            
        self.stdout.write(self.style.SUCCESS('Successfully populated Ambulance test data'))
