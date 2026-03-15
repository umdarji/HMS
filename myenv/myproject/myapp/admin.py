from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Admin, Doctor, Patient, Department, Staff, OPDAppointment, IPDAdmission, Payment, OTP, Bed, DoctorSchedule

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone')}),
    )

# Admin Model
@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')

# Doctor Model
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('doctor_id', 'first_name', 'last_name', 'specialization', 'department', 'phone', 'availability_status', 'created_at')
    list_filter = ('specialization', 'department', 'availability_status', 'is_first_login', 'created_at')
    search_fields = ('doctor_id', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('doctor_id', 'created_at')
    
    fieldsets = (
        ('Doctor Information', {
            'fields': ('doctor_id', 'first_name', 'last_name', 'department', 'specialization', 'availability_status')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email')
        }),
        ('Account', {
            'fields': ('user', 'is_first_login', 'created_at')
        }),
    )

# Patient Model
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'name', 'age', 'gender', 'phone', 'created_at')
    list_filter = ('gender', 'blood_group', 'created_at')
    search_fields = ('patient_id', 'name', 'email', 'phone')
    readonly_fields = ('patient_id', 'created_at')
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_id', 'name', 'age', 'gender', 'blood_group', 'id_proof_number')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'address', 'emergency_contact')
        }),
        ('Account', {
            'fields': ('user', 'created_at')
        }),
    )

# Department Model
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Staff Model
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'name', 'role', 'department', 'phone', 'joining_date')
    list_filter = ('role', 'department', 'joining_date')
    search_fields = ('staff_id', 'name', 'email', 'phone')
    readonly_fields = ('staff_id', 'joining_date')

# OPD Appointment Model
@admin.register(OPDAppointment)
class OPDAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'token_no', 'visit_type', 'appointment_date', 'status', 'fee')
    list_filter = ('status', 'visit_type', 'appointment_date')
    search_fields = ('patient__name', 'doctor__name', 'reason')
    date_hierarchy = 'appointment_date'

# IPD Admission Model
@admin.register(IPDAdmission)
class IPDAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'ward_no', 'bed', 'status', 'admission_date')
    list_filter = ('status', 'admission_type', 'admission_date')
    search_fields = ('patient__name', 'doctor__name')

# Payment Model
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'amount', 'payment_method', 'payment_date', 'transaction_id')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('patient__name', 'transaction_id')
    date_hierarchy = 'payment_date'

# OTP Model (Optional, for debugging)
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'is_verified', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('otp_code', 'created_at', 'expires_at')

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('ward_type', 'bed_number', 'status', 'daily_charge')
    list_filter = ('ward_type', 'status')
    search_fields = ('bed_number',)

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'doctor')

