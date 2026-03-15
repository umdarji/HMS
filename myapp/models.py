from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('staff', 'Staff'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    name = models.CharField(max_length=200)
    profile_image = models.ImageField(upload_to='profile_images/admin/', blank=True, null=True, default='profile_images/default.png')
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    doctor_id = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    is_first_login = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='profile_images/doctors/', blank=True, null=True, default='profile_images/default.png')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Moved from add_to_class
    availability_status = models.CharField(
        max_length=20, 
        choices=[('Available', 'Available'), ('On Leave', 'On Leave'), ('Emergency', 'Emergency')],
        default='Available'
    )

    def __str__(self):
        return f"{self.doctor_id} - {self.first_name} {self.last_name}"
        
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
    @staticmethod
    def generate_doctor_id():
        last_doctor = Doctor.objects.all().order_by('id').last()
        if last_doctor:
            last_id = int(last_doctor.doctor_id[3:])
            new_id = f"DOC{last_id + 1:03d}"
        else:
            new_id = "DOC001"
        return new_id

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = self.generate_doctor_id()
        super().save(*args, **kwargs)

class Staff(models.Model):
    ROLE_CHOICES = (
        ('Receptionist', 'Receptionist'),
        ('Lab Technician', 'Lab Technician'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff_profile', null=True, blank=True)
    staff_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    profile_image = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.staff_id} - {self.name} ({self.role})"
        
    @staticmethod
    def generate_staff_id():
        last_staff = Staff.objects.all().order_by('id').last()
        if last_staff:
            last_id = int(last_staff.staff_id[3:])
            new_id = f"STF{last_id + 1:03d}"
        else:
            new_id = "STF001"
        return new_id

    def save(self, *args, **kwargs):
        if not self.staff_id:
            self.staff_id = self.generate_staff_id()
        super().save(*args, **kwargs)

class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    patient_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    blood_group = models.CharField(max_length=5, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/patients/', blank=True, null=True, default='profile_images/default.png')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Moved from add_to_class
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    id_proof_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.patient_id} - {self.name}"
    
    @staticmethod
    def generate_patient_id():
        last_patient = Patient.objects.all().order_by('id').last()
        if last_patient:
            last_id = int(last_patient.patient_id[3:])
            new_id = f"PAT{last_id + 1:03d}"
        else:
            new_id = "PAT001"
        return new_id

    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = self.generate_patient_id()
        super().save(*args, **kwargs)



class OPDAppointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Moved from add_to_class
    token_no = models.IntegerField(null=True, blank=True)
    visit_type = models.CharField(
        max_length=20, 
        choices=[('New', 'New'), ('Follow-up', 'Follow-up')], 
        default='New'
    )

    def __str__(self):
        doctor_name = self.doctor.name if self.doctor else "Unknown Doctor"
        return f"OPD - {self.patient.name} with {doctor_name}"

class Bed(models.Model):
    WARD_CHOICES = (
        ('General', 'General Ward Bed'),
        ('SemiPrivate', 'Semi-Private Bed'),
        ('Private', 'Private Room Bed'),
        ('Deluxe', 'Deluxe / Suite Bed'),
        ('ICU', 'ICU Bed'),
        ('CCU', 'CCU Bed'),
        ('NICU', 'NICU Bed'),
        ('PICU', 'PICU Bed'),
        ('HDU', 'HDU Bed'),
        ('Emergency', 'Emergency Bed'),
        ('Recovery', 'Recovery Bed'),
        ('PostOp', 'Post-Op Bed'),
        ('Orthopedic', 'Orthopedic Bed'),
    )
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Maintenance', 'Maintenance'),
    )
    ward_type = models.CharField(max_length=20, choices=WARD_CHOICES)
    bed_number = models.CharField(max_length=10, unique=True)
    daily_charge = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    
    def __str__(self):
        return f"{self.ward_type} - {self.bed_number} ({self.status})"

class IPDAdmission(models.Model):
    STATUS_CHOICES = (
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    admission_date = models.DateTimeField(auto_now_add=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    ward_no = models.CharField(max_length=50)
    bed_no = models.CharField(max_length=50)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Admitted')
    
    # Moved from add_to_class
    admission_type = models.CharField(
        max_length=20, 
        choices=[('Emergency', 'Emergency'), ('Planned', 'Planned')],
        default='Planned'
    )
    expected_discharge_date = models.DateField(null=True, blank=True)
    is_discharge_requested = models.BooleanField(default=False)
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"IPD - {self.patient.name} (Bed: {self.bed_no})"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('Cash', 'Cash'),
        ('Online', 'Online'),
        ('Insurance', 'Insurance'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, help_text="Reason for payment (e.g. Consultation, Medicine, Bed Charge)")
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Razorpay Fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.patient.name} - {self.amount}"

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"
    
    class Meta:
        ordering = ['-created_at']

# ============ NEW MODELS FOR RECEPTIONIST DASHBOARD ============

class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"{self.doctor.name} - {self.day_of_week}"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.ForeignKey(OPDAppointment, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.TextField()
    medicines = models.TextField(help_text="Medicine name, dose, duration")
    advice = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.name} by {self.doctor.name}"

class LabReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=200)
    requested_date = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to='lab_reports/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Uploaded', 'Uploaded')], default='Pending')
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.test_name} for {self.patient.name}"

class ChatSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True) # For anonymous users
    started_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat {self.session_id}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender}: {self.message[:20]}"

class DischargeSummary(models.Model):
    admission = models.OneToOneField(IPDAdmission, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    treatment_given = models.TextField()
    final_advice = models.TextField()
    follow_up_plan = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Discharge Summary - {self.patient.name}"
