import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import CustomUser, Doctor, Patient, Department, OPDAppointment, IPDAdmission, Bed, Prescription, LabReport
from datetime import timedelta
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # 1. Departments
        depts = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'General Medicine', 'Dermatology']
        dept_objs = []
        for d in depts:
            dept, _ = Department.objects.get_or_create(name=d)
            dept_objs.append(dept)
            
        # 2. Doctors (Create only if needed to avoid dupes, but for demo we can create a specific one)
        # Ensure our logged in doctor (if any) exists or create new ones
        
        # 3. Patients (Create 20 dummy patients)
        first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        patients = []
        for i in range(20):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            phone = f"9876543{i:03d}"
            
            if not Patient.objects.filter(phone=phone).exists():
                # Create User
                user = CustomUser.objects.create_user(
                    username=f"pat{i}", 
                    email=f"pat{i}@example.com", 
                    password="password123", 
                    user_type='patient',
                    phone=phone
                )
                
                patient = Patient.objects.create(
                    user=user,
                    name=name,
                    age=random.randint(5, 80),
                    gender=random.choice(['Male', 'Female']),
                    phone=phone,
                    email=f"pat{i}@example.com",
                    address="123 Dummy St, City"
                )
                patients.append(patient)
            else:
                patients.append(Patient.objects.get(phone=phone))
                
        self.stdout.write(f'Created/Found {len(patients)} patients')

        # 4. Create Appointments for Today (for ALL Doctors)
        doctors = Doctor.objects.all()
        if not doctors.exists():
            # Create a demo doctor if none exist
            u = CustomUser.objects.create_user('doc_demo', 'doc@demo.com', 'password123', user_type='doctor')
            d = Doctor.objects.create(
                user=u, 
                name='Dr. Demo', 
                specialization='General Physician', 
                department=dept_objs[0],
                phone='9999999999',
                email='doc@demo.com'
            )
            doctors = [d]
            
        today = timezone.now().replace(hour=9, minute=0, second=0)
        
        for doctor in doctors:
            self.stdout.write(f'Creating appointments for {doctor.name}...')
            # Create 5 appointments for TODAY for THIS doctor
            for i in range(5):
                OPDAppointment.objects.create(
                    patient=random.choice(patients),
                    doctor=doctor,
                    appointment_date=today + timedelta(hours=i),
                    reason=random.choice(['Fever', 'Headache', 'Stomach Pain', 'Routine Checkup']),
                    status='Pending',
                    visit_type=random.choice(['New', 'Follow-up']),
                    token_no=i+1
                )
                
            # Create some completed ones from yesterday
            yesterday = today - timedelta(days=1)
            for i in range(5):
                 OPDAppointment.objects.create(
                    patient=random.choice(patients),
                    doctor=doctor,
                    appointment_date=yesterday + timedelta(hours=i),
                    reason='Follow up',
                    status='Completed',
                    visit_type='Follow-up'
                )
            
        self.stdout.write('Created Appointments for all doctors')
        
        # 5. IPD Admissions
        # Create Beds first
        ward_types = ['General', 'Private', 'ICU']
        beds = []
        for i in range(10):
            b, _ = Bed.objects.get_or_create(
                bed_number=f"B-{100+i}",
                defaults={'ward_type': random.choice(ward_types), 'daily_charge': 500, 'status': 'Available'}
            )
            beds.append(b)
            
        # Admit 3 patients
        for i in range(3):
            bed = beds[i]
            if bed.status == 'Available':
                IPDAdmission.objects.create(
                    patient=patients[i],
                    doctor=doctor,
                    ward_no=bed.ward_type,
                    bed_no=bed.bed_number,
                    bed=bed,
                    reason='Severe fever requiring observation',
                    status='Admitted',
                    admission_type='Emergency'
                )
                bed.status = 'Occupied'
                bed.save()
                
        # 6. Lab Reports (Pending)
        for i in range(2):
            LabReport.objects.create(
                patient=random.choice(patients),
                doctor=doctor,
                test_name=random.choice(['CBC', 'X-Ray', 'Typhoid Test']),
                status='Pending'
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded database with dummy data!'))
