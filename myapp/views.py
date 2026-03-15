from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .otp_utils import create_otp, verify_otp
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.core.mail import send_mail
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import uuid
import re
import json

# ============ UNIFIED LOGIN WITH OTP ============

def unified_login_view(request):
    """Single login page for all user types with OTP option"""
    if request.method == 'POST':
        role = request.POST.get('role')
        username = request.POST.get('username')
        
        user = None
        
        # Look up user based on role and input (ID/Username/Email/Phone)
        if role == 'admin':
            # Try Username
            try:
                user = CustomUser.objects.get(username=username, user_type='admin')
            except CustomUser.DoesNotExist:
                # Try Email
                try:
                    user = CustomUser.objects.get(email=username, user_type='admin')
                except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
                    # Try Phone
                    try:
                        user = CustomUser.objects.get(phone=username, user_type='admin')
                    except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
                        pass
                    
        elif role == 'doctor':
            try:
                # Try Doctor ID
                doctor = Doctor.objects.get(doctor_id=username)
                user = doctor.user
            except Doctor.DoesNotExist:
                try:
                    # Try Email
                    doctor = Doctor.objects.get(email=username)
                    user = doctor.user
                except (Doctor.DoesNotExist, Doctor.MultipleObjectsReturned):
                    try:
                        # Try Phone
                        doctor = Doctor.objects.get(phone=username)
                        user = doctor.user
                    except (Doctor.DoesNotExist, Doctor.MultipleObjectsReturned):
                        pass
                
        elif role == 'patient':
            # Patient can login via ID, Email, or Phone
            try:
                # Try Patient ID
                patient = Patient.objects.get(patient_id=username)
                user = patient.user
            except Patient.DoesNotExist:
                try:
                    # Try Email
                    patient = Patient.objects.get(email=username)
                    user = patient.user
                except (Patient.DoesNotExist, Patient.MultipleObjectsReturned):
                    try:
                        # Try Phone
                        patient = Patient.objects.get(phone=username)
                        user = patient.user
                    except (Patient.DoesNotExist, Patient.MultipleObjectsReturned):
                        pass

        elif role == 'staff':
            # Staff can login via ID, Email, or Phone
            try:
                # Try Staff ID
                staff = Staff.objects.get(staff_id=username)
                user = staff.user
            except Staff.DoesNotExist:
                try:
                    # Try Email
                    staff = Staff.objects.get(email=username)
                    user = staff.user
                except (Staff.DoesNotExist, Staff.MultipleObjectsReturned):
                    try:
                        # Try Phone
                        staff = Staff.objects.get(phone=username)
                        user = staff.user
                    except (Staff.DoesNotExist, Staff.MultipleObjectsReturned):
                        pass
        
        if user and user.user_type == role:
            create_otp(user)
            request.session['otp_user_id'] = user.id
            request.session['otp_email'] = user.email
            return redirect('verify_otp')
        
        return render(request, 'myapp/auth/login.html', {
            'error': 'User not found or invalid role. Please verify your ID/Email and Role.',
            'role': role
        })
    
    return render(request, 'myapp/auth/login.html')

def verify_otp_view(request):
    """OTP verification page"""
    user_id = request.session.get('otp_user_id')
    email = request.session.get('otp_email', 'your email')
    
    if not user_id:
        return redirect('login')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(id=user_id)
            success, message = verify_otp(user, otp_code)
            
            if success:
                login(request, user)
                # Clear session
                request.session.pop('otp_user_id', None)
                request.session.pop('otp_email', None)
                
                # Redirect based on user type
                if user.user_type == 'admin':
                    return redirect('admin_dashboard')
                elif user.user_type == 'doctor':
                    return redirect('doctor_dashboard')
                elif user.user_type == 'staff':
                    return redirect('staff_dashboard')
                else:
                    return redirect('patient_dashboard')
            else:
                return render(request, 'myapp/auth/otp_verify.html', {
                    'error': message,
                    'email': email
                })
        except CustomUser.DoesNotExist:
            return redirect('login')
    
    return render(request, 'myapp/auth/otp_verify.html', {'email': email})

def resend_otp_view(request):
    """Resend OTP"""
    user_id = request.session.get('otp_user_id')
    if user_id:
        try:
            user = CustomUser.objects.get(id=user_id)
            create_otp(user)
        except CustomUser.DoesNotExist:
            pass
    return redirect('verify_otp')

# ============ PATIENT REGISTRATION ============

def patient_register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group', '')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            return render(request, 'myapp/auth/patient_register.html', {'error': 'Passwords do not match'})
        
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'myapp/auth/patient_register.html', {'error': 'Email already registered'})
        
        patient_id = Patient.generate_patient_id()
        user = CustomUser.objects.create_user(
            username=patient_id,
            email=email,
            password=password,
            user_type='patient',
            phone=phone
        )
        
        Patient.objects.create(
            user=user,
            patient_id=patient_id,
            name=name,
            age=age,
            gender=gender,
            blood_group=blood_group,
            phone=phone,
            email=email,
            address=address
        )
        
        return render(request, 'myapp/auth/patient_register.html', {
            'success': f'Registration successful! Your Patient ID is: {patient_id}. Please login.'
        })
    
    return render(request, 'myapp/auth/patient_register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ============ ADMIN VIEWS ============

@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    
    today = timezone.localdate()
    
    # Stats
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = OPDAppointment.objects.count()
    
    # Revenue Calculation
    pay_rev = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    opd_rev = OPDAppointment.objects.aggregate(Sum('fee'))['fee__sum'] or 0
    total_revenue = pay_rev + opd_rev
    
    # Recent Data
    recent_appointments = OPDAppointment.objects.filter(appointment_date__date=today).order_by('-appointment_date')[:10]
    recent_patients = Patient.objects.all().order_by('-id')[:5]
    
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'recent_appointments': recent_appointments,
        'recent_patients': recent_patients,
        'opd_count': total_appointments,
        'ipd_count': IPDAdmission.objects.count(),
    }
    
    return render(request, "myapp/admin/admin_dashboard.html", context)

@login_required
def admin_doctors(request):
    """List all doctors"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    doctors = Doctor.objects.all().order_by('-id')
    departments = Department.objects.all()
    return render(request, "myapp/admin/doctors.html", {
        'doctors': doctors,
        'departments': departments
    })

@login_required
def admin_add_doctor(request):
    """Add new doctor"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        specialization = request.POST.get('specialization')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        department_id = request.POST.get('department')
        
        # Validation
        if Doctor.objects.filter(email=email).exists():
            doctors = Doctor.objects.all().order_by('-id')
            departments = Department.objects.all()
            return render(request, "myapp/admin/doctors.html", {
                'doctors': doctors,
                'departments': departments,
                'error': 'Doctor with this email already exists.'
            })
        
        if Doctor.objects.filter(phone=phone).exists():
            doctors = Doctor.objects.all().order_by('-id')
            departments = Department.objects.all()
            return render(request, "myapp/admin/doctors.html", {
                'doctors': doctors,
                'departments': departments,
                'error': 'Doctor with this phone already exists.'
            })
        
        try:
            doctor_id = Doctor.generate_doctor_id()
            temp_password = f"doctor{doctor_id[-3:]}"
            
            user = CustomUser.objects.create_user(
                username=doctor_id,
                email=email,
                password=temp_password,
                user_type='doctor',
                phone=phone
            )
            
            department = Department.objects.get(id=department_id) if department_id else None
            
            Doctor.objects.create(
                user=user,
                doctor_id=doctor_id,
                first_name=first_name,
                last_name=last_name,
                specialization=specialization,
                phone=phone,
                email=email,
                department=department
            )
            
            doctors = Doctor.objects.all().order_by('-id')
            departments = Department.objects.all()
            return render(request, "myapp/admin/doctors.html", {
                'doctors': doctors,
                'departments': departments,
                'success': f'Doctor created successfully! ID: {doctor_id}, Temporary Password: {temp_password}'
            })
        except Exception as e:
            doctors = Doctor.objects.all().order_by('-id')
            departments = Department.objects.all()
            return render(request, "myapp/admin/doctors.html", {
                'doctors': doctors,
                'departments': departments,
                'error': f'Error creating doctor: {str(e)}'
            })
    
    return redirect('admin_doctors')


@login_required
def admin_staff(request):
    """List all staff members"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    staff_members = Staff.objects.all().order_by('-id')
    
    context = {
        'staff_members': staff_members,
    }
    
    return render(request, "myapp/admin/staff.html", context)

@login_required
def admin_edit_doctor(request, id):
    """Edit existing doctor"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    try:
        doctor = Doctor.objects.get(id=id)
    except Doctor.DoesNotExist:
        return redirect('admin_doctors')
    
    departments = Department.objects.all()

    if request.method == 'POST':
        doctor.first_name = request.POST.get('first_name')
        doctor.last_name = request.POST.get('last_name')
        doctor.specialization = request.POST.get('specialization')
        doctor.phone = request.POST.get('phone')
        doctor.email = request.POST.get('email')
        department_id = request.POST.get('department')
        availability_status = request.POST.get('availability_status')
        
        # Update department if provided
        if department_id:
            try:
                doctor.department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                pass
        else:
            doctor.department = None
        
        # Update availability status if provided
        if availability_status:
            doctor.availability_status = availability_status
        
        # Update user email and phone
        if doctor.user:
            doctor.user.email = doctor.email
            doctor.user.phone = doctor.phone
            doctor.user.save()
        
        doctor.save()
        
        return redirect('admin_doctors')
    
    return render(request, "myapp/admin/doctors/edit.html", {'doctor': doctor, 'departments': departments})

@login_required
def admin_view_doctor(request, id):
    """View doctor details (returns JSON for modal)"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    from django.http import JsonResponse
    try:
        doctor = Doctor.objects.get(id=id)
        data = {
            'id': doctor.id,
            'doctor_id': doctor.doctor_id,
            'name': doctor.name,
            'specialization': doctor.specialization,
            'department': doctor.department.name if doctor.department else 'N/A',
            'phone': doctor.phone,
            'email': doctor.email,
            'availability_status': doctor.availability_status,
            'created_at': doctor.created_at.strftime('%Y-%m-%d %H:%M')
        }
        return JsonResponse(data)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

@login_required
def admin_delete_doctor(request, id):
    """Delete doctor"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    try:
        doctor = Doctor.objects.get(id=id)
        doctor_name = doctor.name
        user = doctor.user
        doctor.delete()
        if user:
            user.delete()
        
        doctors = Doctor.objects.all().order_by('-id')
        departments = Department.objects.all()
        return render(request, "myapp/admin/doctors.html", {
            'doctors': doctors,
            'departments': departments,
            'success': f'Doctor {doctor_name} deleted successfully!'
        })
    except Doctor.DoesNotExist:
        pass
    
    return redirect('admin_doctors')

@login_required
def admin_doctors_pdf(request):
    """Generate PDF of all doctors"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from io import BytesIO
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Add title
    title = Paragraph("Hospital Management System - All Doctors", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Get all doctors
    doctors = Doctor.objects.all().order_by('-id')
    
    # Prepare table data
    data = [['ID', 'Name', 'Specialization', 'Department', 'Phone', 'Email', 'Status']]
    
    for doctor in doctors:
        data.append([
            doctor.doctor_id,
            doctor.name[:25],  # Truncate if too long
            doctor.specialization[:20],
            (doctor.department.name[:15] if doctor.department else 'N/A'),
            doctor.phone,
            doctor.email[:30],  # Truncate if too long
            doctor.availability_status
        ])
    
    # Create table
    table = Table(data, colWidths=[0.8*inch, 1.8*inch, 1.5*inch, 1.2*inch, 1.2*inch, 2*inch, 1*inch])
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    
    # Add footer info
    elements.append(Spacer(1, 20))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=TA_CENTER)
    footer_text = f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Doctors: {doctors.count()}"
    footer = Paragraph(footer_text, footer_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF from buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="all_doctors_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    response.write(pdf)
    
    return response


@login_required
def admin_patients(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    patients = Patient.objects.all().order_by('-id')
    return render(request, "myapp/admin/patients.html", {'patients': patients})

@login_required
def admin_appointments(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    # Fetch all appointments ordered by date (newest first)
    appointments = OPDAppointment.objects.all().order_by('-appointment_date')
    return render(request, "myapp/admin/appointments.html", {'appointments': appointments})

@login_required
def admin_billing(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    # Fetch all payments ordered by date (newest first)
    payments = Payment.objects.all().order_by('-payment_date')
    return render(request, "myapp/admin/billing.html", {'payments': payments})

@login_required
def admin_reports(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    
    # Calculate statistics for initial page load
    payment_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    opd_revenue = OPDAppointment.objects.aggregate(Sum('fee'))['fee__sum'] or 0
    total_revenue = float(payment_revenue) + float(opd_revenue)
    
    total_patients = Patient.objects.count()
    total_appointments = OPDAppointment.objects.count()
    
    # Calculate satisfaction rate
    completed_appts = OPDAppointment.objects.filter(status='Completed').count()
    satisfaction_rate = round((completed_appts / total_appointments * 100) if total_appointments > 0 else 0, 1)
    
    context = {
        'total_revenue': total_revenue,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'satisfaction_rate': satisfaction_rate,
    }
    
    return render(request, "myapp/admin/reports.html", context)

@login_required
def admin_profile(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    
    # Get or create admin profile
    try:
        admin = request.user.admin_profile
    except Admin.DoesNotExist:
        admin = Admin.objects.create(
            user=request.user,
            name=request.user.username
        )
    
    if request.method == 'POST':
        # Update profile information
        admin.name = request.POST.get('first_name', '') + ' ' + request.POST.get('last_name', '')
        
        # Handle profile image upload
        if request.FILES.get('profile_image'):
            admin.profile_image = request.FILES['profile_image']
        
        # Update user email and phone if provided
        request.user.email = request.POST.get('email', request.user.email)
        
        admin.save()
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('admin_profile')
    
    # Split name for display
    name_parts = admin.name.split(' ', 1)
    first_name = name_parts[0] if len(name_parts) > 0 else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    context = {
        'admin': admin,
        'first_name': first_name,
        'last_name': last_name,
    }
    
    return render(request, "myapp/admin/profile.html", context)

@login_required
def admin_add_patient(request):
    """Add new patient from admin panel"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        blood_group = request.POST.get('blood_group', '')
        address = request.POST.get('address', '')
        
        # Validation
        if Patient.objects.filter(phone=phone).exists():
            patients = Patient.objects.all().order_by('-id')
            return render(request, "myapp/admin/patients.html", {
                'patients': patients,
                'error': 'Patient with this phone already exists.'
            })
        
        # Generate patient ID and create user
        patient_id = Patient.generate_patient_id()
        password = phone  # Default password
        
        try:
            user = CustomUser.objects.create_user(
                username=patient_id,
                email=email,
                password=password,
                user_type='patient',
                phone=phone
            )
            
            Patient.objects.create(
                user=user,
                patient_id=patient_id,
                name=name,
                age=age,
                gender=gender,
                blood_group=blood_group,
                phone=phone,
                email=email,
                address=address
            )
            
            patients = Patient.objects.all().order_by('-id')
            return render(request, "myapp/admin/patients.html", {
                'patients': patients,
                'success': f'Patient created successfully! ID: {patient_id}'
            })
        except Exception as e:
            patients = Patient.objects.all().order_by('-id')
            return render(request, "myapp/admin/patients.html", {
                'patients': patients,
                'error': f'Error creating patient: {str(e)}'
            })
    
    return redirect('admin_patients')

@login_required
def admin_view_patient(request, id):
    """View patient details (returns JSON for modal)"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    from django.http import JsonResponse
    try:
        patient = Patient.objects.get(id=id)
        data = {
            'patient_id': patient.patient_id,
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'blood_group': patient.blood_group,
            'phone': patient.phone,
            'email': patient.email,
            'address': patient.address,
            'emergency_contact': patient.emergency_contact or 'N/A',
            'id_proof_number': patient.id_proof_number or 'N/A',
            'created_at': patient.created_at.strftime('%Y-%m-%d %H:%M')
        }
        return JsonResponse(data)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

@login_required
def admin_delete_patient(request, id):
    """Delete patient"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    try:
        patient = Patient.objects.get(id=id)
        user = patient.user
        patient.delete()
        if user:
            user.delete()
    except Patient.DoesNotExist:
        pass
    
    return redirect('admin_patients')

@login_required
def admin_patients_pdf(request):
    """Generate PDF of all patients"""
    if request.user.user_type != 'admin':
        return redirect('login')
    
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from io import BytesIO
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Add title
    title = Paragraph("Hospital Management System - All Patients", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Get all patients
    patients = Patient.objects.all().order_by('-id')
    
    # Prepare table data
    data = [['ID', 'Name', 'Age', 'Gender', 'Phone', 'Blood Group', 'Email']]
    
    for patient in patients:
        data.append([
            patient.patient_id,
            patient.name[:20],  # Truncate if too long
            str(patient.age),
            patient.gender,
            patient.phone,
            patient.blood_group or 'N/A',
            patient.email[:25]  # Truncate if too long
        ])
    
    # Create table
    table = Table(data, colWidths=[0.8*inch, 1.8*inch, 0.6*inch, 0.8*inch, 1.2*inch, 1*inch, 2*inch])
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    
    # Add footer info
    elements.append(Spacer(1, 20))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=TA_CENTER)
    footer_text = f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Patients: {patients.count()}"
    footer = Paragraph(footer_text, footer_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF from buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="all_patients_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    response.write(pdf)
    
    return response


# ============ DEPARTMENT VIEWS ============

@login_required
def department_list(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    departments = Department.objects.all()
    return render(request, "myapp/admin/departments/list.html", {'departments': departments})

@login_required
def add_department(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        Department.objects.create(name=name, description=description)
        return redirect('department_list')
    return render(request, "myapp/admin/departments/add.html")

@login_required
def edit_department(request, id):
    if request.user.user_type != 'admin':
        return redirect('login')
    dept = Department.objects.get(id=id)
    if request.method == 'POST':
        dept.name = request.POST.get('name')
        dept.description = request.POST.get('description')
        dept.save()
        return redirect('department_list')
    return render(request, "myapp/admin/departments/edit.html", {'department': dept})

@login_required
def delete_department(request, id):
    if request.user.user_type != 'admin':
        return redirect('login')
    Department.objects.get(id=id).delete()
    return redirect('department_list')

# ============ STAFF VIEWS ============

@login_required
def staff_list(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    staff_members = Staff.objects.all()
    return render(request, "myapp/admin/staff/list.html", {'staff_members': staff_members})

@login_required
def add_staff(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    departments = Department.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        dept_id = request.POST.get('department')
        
        department = Department.objects.get(id=dept_id) if dept_id else None
        
        # Create User for Staff
        staff_id = Staff.generate_staff_id()
        temp_password = f"staff{staff_id[-3:]}"
        
        user = CustomUser.objects.create_user(
            username=staff_id,
            email=email,
            password=temp_password,
            user_type='staff',
            phone=phone
        )
        
        Staff.objects.create(
            user=user,
            staff_id=staff_id,
            name=name,
            role=role,
            department=department,
            phone=phone,
            email=email
        )
        return redirect('staff_list')
    return render(request, "myapp/admin/staff/add.html", {'departments': departments})

@login_required
def edit_staff(request, id):
    if request.user.user_type != 'admin':
        return redirect('login')
    staff = Staff.objects.get(id=id)
    departments = Department.objects.all()
    if request.method == 'POST':
        staff.name = request.POST.get('name')
        staff.email = request.POST.get('email')
        staff.phone = request.POST.get('phone')
        staff.role = request.POST.get('role')
        dept_id = request.POST.get('department')
        
        staff.department = Department.objects.get(id=dept_id) if dept_id else None
        staff.save()
        return redirect('staff_list')
    return render(request, "myapp/admin/staff/edit.html", {'staff': staff, 'departments': departments})

@login_required
def delete_staff(request, id):
    if request.user.user_type != 'admin':
        return redirect('login')
    staff = Staff.objects.get(id=id)
    if staff.user:
        staff.user.delete() # Deletes user and cascades to profile
    else:
        staff.delete()
    return redirect('staff_list')




# ============ OPD VIEWS ============

@login_required
def opd_list(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    appointments = OPDAppointment.objects.all().order_by('-appointment_date')
    return render(request, "myapp/admin/opd/list.html", {'appointments': appointments})

@login_required
def opd_add(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        reason = request.POST.get('reason')
        fee = request.POST.get('fee')
        date = request.POST.get('date')
        
        OPDAppointment.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            reason=reason,
            fee=fee,
            appointment_date=date,
            status='Pending'
        )
        return redirect('opd_list')
    return render(request, "myapp/admin/opd/add.html", {'patients': patients, 'doctors': doctors})

@login_required
def opd_edit(request, id):
    if request.user.user_type != 'admin':
        return redirect('login')
    appointment = OPDAppointment.objects.get(id=id)
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    if request.method == 'POST':
        appointment.doctor_id = request.POST.get('doctor')
        appointment.reason = request.POST.get('reason')
        appointment.fee = request.POST.get('fee')
        appointment.status = request.POST.get('status')
        appointment.save()
        return redirect('opd_list')
    return render(request, "myapp/admin/opd/edit.html", {'appointment': appointment, 'patients': patients, 'doctors': doctors})

# ============ IPD VIEWS ============

@login_required
def ipd_list(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    admissions = IPDAdmission.objects.all().order_by('-admission_date')
    return render(request, "myapp/admin/ipd/list.html", {'admissions': admissions})

@login_required
def ipd_add(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        ward_no = request.POST.get('ward_no')
        bed_no = request.POST.get('bed_no')
        reason = request.POST.get('reason')
        
        IPDAdmission.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            ward_no=ward_no,
            bed_no=bed_no,
            reason=reason,
            status='Admitted'
        )
        return redirect('ipd_list')
    return render(request, "myapp/admin/ipd/add.html", {'patients': patients, 'doctors': doctors})

@login_required
def ipd_discharge(request, id):
    if request.user.user_type != 'admin':
        return redirect('login')
    admission = IPDAdmission.objects.get(id=id)
    if request.method == 'POST':
        admission.status = 'Discharged'
        admission.discharge_date = timezone.now()
        admission.save()
        return redirect('ipd_list')
    return render(request, "myapp/admin/ipd/discharge.html", {'admission': admission})

# ============ PAYMENT VIEWS ============

@login_required
def payment_list(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    payments = Payment.objects.all().order_by('-payment_date')
    return render(request, "myapp/admin/payments/list.html", {'payments': payments})

@login_required
def add_payment(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    patients = Patient.objects.all()
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        description = request.POST.get('description')
        
        Payment.objects.create(
            patient_id=patient_id,
            amount=amount,
            payment_method=payment_method,
            description=description
        )
        return redirect('payment_list')
    return render(request, "myapp/admin/payments/add.html", {'patients': patients})

# ============ STAFF VIEWS ============

@login_required
def staff_dashboard(request):
    if request.user.user_type != 'staff':
        return redirect('login')
    
    # Ensure staff profile exists
    if not hasattr(request.user, 'staff_profile'):
        return render(request, "myapp/staff/error.html", {'message': 'Staff profile not found.'})
        
    role = request.user.staff_profile.role
    
    if role == 'Receptionist':
        return redirect('receptionist_dashboard')
    elif role == 'Lab Technician':
        return redirect('laboratory_dashboard')
        
    context = {'role': role}
    context = {'role': role}
    return render(request, "myapp/staff/dashboard.html", context)

# --- Laboratory Views ---

@login_required
def laboratory_dashboard(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Lab Technician':
        return redirect('login')
    
    # Stats
    pending_tests_count = LabReport.objects.filter(status='Pending').count()
    completed_today = LabReport.objects.filter(status='Uploaded', requested_date__date=timezone.localdate()).count()
    
    # Lists
    pending_tests = LabReport.objects.filter(status='Pending').order_by('requested_date')
    recent_uploads = LabReport.objects.filter(status='Uploaded').order_by('-requested_date')[:5]
    
    # For Add Test Modal
    patients = Patient.objects.all().order_by('name')
    doctors = Doctor.objects.filter(availability_status='Available')
    
    context = {
        'pending_tests_count': pending_tests_count,
        'completed_today': completed_today,
        'pending_tests': pending_tests,
        'recent_uploads': recent_uploads,
        'patients': patients,
        'doctors': doctors,
    }
    
    return render(request, "myapp/staff/laboratory/dashboard.html", context)

@login_required
def laboratory_upload_report(request, id):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Lab Technician':
        return redirect('login')
        
    report = get_object_or_404(LabReport, id=id)
    
    if request.method == 'POST':
        if 'report_file' in request.FILES:
            report.report_file = request.FILES['report_file']
            report.status = 'Uploaded'
            report.remarks = request.POST.get('remarks', '')
            report.save()
            messages.success(request, 'Report uploaded successfully!')
        else:
            messages.error(request, 'Please select a file to upload.')
            
        return redirect('laboratory_dashboard')
        
    return redirect('laboratory_dashboard')

@login_required
def laboratory_add_test(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Lab Technician':
        return redirect('login')
        
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        test_name = request.POST.get('test_name')
        doctor_id = request.POST.get('doctor')
        
        try:
            # If no doctor selected, we might fail since model requires it.
            # Assuming form enforces it or we pick a random one/default.
            # Let's enforce it in template.
            doctor = Doctor.objects.get(id=doctor_id)
            
            LabReport.objects.create(
                patient_id=patient_id,
                doctor=doctor,
                test_name=test_name,
                status='Pending'
            )
            messages.success(request, 'Test request added successfully.')
        except Exception as e:
            messages.error(request, f'Error adding test: {e}')
            
        return redirect('laboratory_dashboard')
    
    return redirect('laboratory_dashboard')

# --- Receptionist Views ---

@login_required
def receptionist_dashboard(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
        
    today = timezone.localdate()
    
    # Stats logic
    opd_today = OPDAppointment.objects.filter(appointment_date__date=today).count()
    ipd_today = IPDAdmission.objects.filter(admission_date__date=today).count()
    # "Today Appointments" might mean OPD or scheduled appointments. Let's assume OPD for now as "appointments" usually refers to that. 
    # Or strict "Appointments" module vs "OPD". Let's use OPD count mostly or check distinct patients.
    appointments_today = opd_today 
    
    available_doctors = Doctor.objects.filter(availability_status='Available').count()
    
    # "Pending Discharge Requests"
    pending_discharges = IPDAdmission.objects.filter(is_discharge_requested=True, status='Admitted').count()
    
    # Recent Activity
    recent_opd = OPDAppointment.objects.all().order_by('-appointment_date')[:5]
    recent_ipd = IPDAdmission.objects.all().order_by('-admission_date')[:5]
    
    context = {
        'opd_today': opd_today,
        'ipd_today': ipd_today,
        'appointments_today': appointments_today,
        'available_doctors': available_doctors,
        'pending_discharges': pending_discharges,
        'recent_opd': recent_opd,
        'recent_ipd': recent_ipd,
    }
    
    return render(request, "myapp/staff/receptionist/dashboard.html", context)


@login_required
def receptionist_appointments(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    # Reuse admin or doctor logic later, placeholder for now
    appointments = OPDAppointment.objects.all().order_by('-appointment_date')
    return render(request, "myapp/staff/receptionist/appointments.html", {'appointments': appointments})

@login_required
def receptionist_add_patient(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        email = request.POST.get('email') or f"{phone}@hospital.local" # Fallback if no email
        address = request.POST.get('address')
        emergency_contact = request.POST.get('emergency_contact')
        id_proof = request.POST.get('id_proof')
        blood_group = request.POST.get('blood_group', '')
        
        # Validation (basic)
        if Patient.objects.filter(phone=phone).exists():
             return render(request, "myapp/staff/receptionist/add_patient.html", {'error': 'Patient with this phone already exists.', 'form_data': request.POST})
             
        patient_id = Patient.generate_patient_id()
        # Create User logic (could differ from public registration)
        # Using phone as password default or something simple
        password = phone 
        
        try:
            user = CustomUser.objects.create_user(
                username=patient_id,
                email=email,
                password=password,
                user_type='patient',
                phone=phone
            )
            
            Patient.objects.create(
                user=user,
                patient_id=patient_id,
                name=name,
                age=age,
                gender=gender,
                blood_group=blood_group,
                phone=phone,
                email=email,
                address=address,
                emergency_contact=emergency_contact,
                id_proof_number=id_proof
            )
            
            return render(request, "myapp/staff/receptionist/add_patient.html", {'success': f'Patient Registered Successfully! ID: {patient_id}'})
            
        except Exception as e:
            return render(request, "myapp/staff/receptionist/add_patient.html", {'error': f'Error registering patient: {str(e)}', 'form_data': request.POST})

    return render(request, "myapp/staff/receptionist/add_patient.html")

@login_required
def receptionist_opd_register(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    
    patients = Patient.objects.all().order_by('-id') # Latest first
    doctors = Doctor.objects.filter(availability_status='Available') # Show only available doctors
    departments = Department.objects.all()
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        visit_type = request.POST.get('visit_type')
        reason = request.POST.get('reason')
        fee = request.POST.get('fee', '500') # Default fee
        
        try:
             # Generate Token (Simple auto-increment for the day)
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            token_count = OPDAppointment.objects.filter(appointment_date__gte=today_start).count()
            token_no = token_count + 1
            
            appointment = OPDAppointment.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=timezone.now(),
                reason=reason,
                status='Pending',
                fee=fee,
                visit_type=visit_type,
                token_no=token_no
            )
            
            return redirect('receptionist_opd_slip', id=appointment.id)
            
        except Exception as e:
            return render(request, "myapp/staff/receptionist/opd_registration.html", {
                'patients': patients, 
                'doctors': doctors, 
                'departments': departments,
                'error': f"Error creating OPD entry: {str(e)}"
            })

    return render(request, "myapp/staff/receptionist/opd_registration.html", {
        'patients': patients, 
        'doctors': doctors,
        'departments': departments
    })

@login_required
def receptionist_opd_slip(request, id):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    
    appointment = OPDAppointment.objects.get(id=id)
    return render(request, "myapp/staff/receptionist/opd_slip.html", {'appointment': appointment})

@login_required
def receptionist_opd_list(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    
    query = request.GET.get('search', '')
    appointments = OPDAppointment.objects.all().order_by('-appointment_date')
    
    if query:
        appointments = appointments.filter(
            Q(patient__name__icontains=query) |
            Q(patient__patient_id__icontains=query) |
            Q(doctor__name__icontains=query) |
            Q(token_no__icontains=query)
        )
            
    return render(request, "myapp/staff/receptionist/opd_list.html", {'appointments': appointments, 'search_query': query})


@login_required
def receptionist_ipd_admit(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
        
    patients = Patient.objects.all().order_by('-id')
    doctors = Doctor.objects.filter(availability_status='Available')
    beds = Bed.objects.filter(status='Available')
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        admission_type = request.POST.get('admission_type')
        reason = request.POST.get('reason')
        bed_id = request.POST.get('bed')
        
        try:
             # Transaction atomic suggested but keeping simple
            bed = Bed.objects.get(id=bed_id)
            
            # Create Admission
            IPDAdmission.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id,
                bed=bed, # Link to Bed model
                ward_no=bed.ward_type, # redundancy for easy access
                bed_no=bed.bed_number, # redundancy
                reason=reason,
                status='Admitted',
                admission_type=admission_type
            )
            
            # Update Bed Status
            bed.status = 'Occupied'
            bed.save()
            
            return redirect('receptionist_ipd_list')
            
        except Exception as e:
            return render(request, "myapp/staff/receptionist/ipd_admission.html", {
                'patients': patients, 'doctors': doctors, 'beds': beds, 'error': str(e)
            })

    return render(request, "myapp/staff/receptionist/ipd_admission.html", {
        'patients': patients, 
        'doctors': doctors,
        'beds': beds,
        'ward_types': Bed.WARD_CHOICES
    })

@login_required
def receptionist_ipd_list(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
        
    query = request.GET.get('search', '')
    admissions = IPDAdmission.objects.filter(status='Admitted').order_by('-admission_date')
    
    if query:
        admissions = admissions.filter(
            Q(patient__name__icontains=query) |
            Q(patient__patient_id__icontains=query) |
            Q(doctor__name__icontains=query) |
            Q(bed_no__icontains=query) |
            Q(ward_no__icontains=query)
        )
            
    return render(request, "myapp/staff/receptionist/ipd_list.html", {'admissions': admissions, 'search_query': query})

@login_required
def receptionist_discharge(request, id):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    
    admission = IPDAdmission.objects.get(id=id)
    if request.method == 'POST':
        admission.is_discharge_requested = True
        admission.expected_discharge_date = request.POST.get('expected_date')
        admission.save()
        return redirect('receptionist_ipd_list')
        
    return render(request, "myapp/staff/receptionist/discharge_request.html", {'admission': admission})

@login_required
def receptionist_finalize_discharge(request, id):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    
    admission = get_object_or_404(IPDAdmission, id=id)
    
    if request.method == 'POST':
        # 1. Update Admission Status
        admission.status = 'Discharged'
        # Check if discharge_date already set? If not use now.
        if not admission.discharge_date:
             admission.discharge_date = timezone.now()
        admission.save()
        
        # 2. Free the Bed
        if admission.bed:
            admission.bed.status = 'Available'
            admission.bed.save()
            
        messages.success(request, f'Patient {admission.patient.name} discharged successfully.')
        return redirect('receptionist_ipd_list')
        
    # Confirmation Page (optional, but good practice)
    return render(request, "myapp/staff/receptionist/discharge_finalize.html", {'admission': admission})

@login_required
def receptionist_book_appt(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
        
    patients = Patient.objects.all().order_by('-id')
    doctors = Doctor.objects.all()
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date') # Date
        time_str = request.POST.get('time') # Time
        reason = request.POST.get('reason')
        
        # Combine date and time
        from datetime import datetime
        appointment_datetime_str = f"{date_str} {time_str}"
        # Make it naive or aware? Django uses aware usually.
        # Simple for now:
        try:
             # Check for slot clash
             # Assuming 15 min slots or just strict equality
             # A real system needs better slot logic.
             # We will check if any appointment exists for this doctor within +/- 15 mins
            
            # Parsing date
            # appointment_datetime = datetime.strptime(appointment_datetime_str, '%Y-%m-%d %H:%M') 
            # Using django timezone for aware
            # For simplicity, let's rely on exact string matching or simplified check for now as 'Slot clash' in requirements might be basic.
            
            # Let's just create it for now as "Pending"
            
            OPDAppointment.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_datetime_str, # Django auto parses often if standard format
                reason=reason,
                status='Pending',
                visit_type='New', # Default or ask?
                fee=500, # Default
                token_no=0 # Scheduled appointments get number later? Or now?
            )
            return redirect('receptionist_appointments')
        except Exception as e:
             return render(request, "myapp/staff/receptionist/book_appointment.html", {
                'patients': patients, 'doctors': doctors, 'error': f"Error booking: {e}"
            })

    return render(request, "myapp/staff/receptionist/book_appointment.html", {
        'patients': patients, 
        'doctors': doctors
    })

@login_required
def receptionist_reschedule_appt(request, id):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
        
    appointment = get_object_or_404(OPDAppointment, id=id)
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        reason = request.POST.get('reason')
        
        try:
            # Combine date and time
            appointment_datetime_str = f"{date_str} {time_str}"
            
            # Update fields
            appointment.appointment_date = appointment_datetime_str
            if reason:
                appointment.reason = reason
            
            # If status was completed/cancelled, maybe reset to pending? 
            # For now, let's assume we just move the time.
            # But if it was cancelled, rescheduling usually implies re-activating.
            if appointment.status == 'Cancelled':
                appointment.status = 'Pending'
                
            appointment.save()
            messages.success(request, 'Appointment rescheduled successfully!')
            return redirect('receptionist_appointments')
            
        except Exception as e:
            return render(request, "myapp/staff/receptionist/reschedule_appointment.html", {
                'appointment': appointment,
                'error': f"Error rescheduling: {str(e)}"
            })
            
    return render(request, "myapp/staff/receptionist/reschedule_appointment.html", {'appointment': appointment})

@login_required
def receptionist_cancel_appt(request, id):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
        
    appointment = get_object_or_404(OPDAppointment, id=id)
    
    if request.method == 'POST':
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('receptionist_appointments')
        
    return render(request, "myapp/staff/receptionist/cancel_appointment.html", {'appointment': appointment})

@login_required
def receptionist_doctor_schedule(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    
    doctors = Doctor.objects.all().order_by('department')
    # If using DoctorSchedule model:
    # schedules = DoctorSchedule.objects.all()
    # But for now, just list doctors and availability status
    return render(request, "myapp/staff/receptionist/doctor_schedule.html", {'doctors': doctors})

@login_required
def receptionist_update_doctor_status(request, id):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
        
    doctor = get_object_or_404(Doctor, id=id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            doctor.availability_status = new_status
            doctor.save()
            messages.success(request, f"Status for Dr. {doctor.name} updated to {new_status}")
            return redirect('receptionist_doctor_schedule')
            
    return render(request, 'myapp/staff/receptionist/doctor_status_edit.html', {'doctor': doctor})

@login_required
def receptionist_billing_view(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    
    # OPD Bills (Appointments with fees)
    opd_bills = OPDAppointment.objects.all().order_by('-appointment_date')
    
    # IPD Bills (Admitted patients) - In real app, separate Bill model linked to Admission
    # For now, just listing admissions
    ipd_bills = IPDAdmission.objects.all().order_by('-admission_date')
    
    # Payments
    payments = Payment.objects.all().order_by('-payment_date')
    
    return render(request, "myapp/staff/receptionist/billing_view.html", {
        'opd_bills': opd_bills,
        'ipd_bills': ipd_bills,
        'payments': payments
    })

@login_required
def receptionist_profile(request):
    if request.user.user_type != 'staff' or request.user.staff_profile.role != 'Receptionist':
        return redirect('login')
    
    staff = request.user.staff_profile
    
    if request.method == 'POST':
        # Handle profile update
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        profile_image = request.FILES.get('profile_image')
        
        if first_name and last_name:
            staff.name = f"{first_name} {last_name}"
        if phone:
            staff.phone = phone
        if profile_image:
            staff.profile_image = profile_image
        staff.save()
        
        if email:
            request.user.email = email
            request.user.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('receptionist_profile')
    
    # Split name into first_name and last_name
    name_parts = staff.name.split(' ', 1) if staff.name else ['', '']
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    context = {
        'staff': staff,
        'first_name': first_name,
        'last_name': last_name
    }
    
    return render(request, 'myapp/staff/receptionist/profile.html', context)







# ============ DOCTOR VIEWS ============

@login_required
def doctor_dashboard(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    return render(request, "myapp/doctor/doctor_dashboard.html")

@login_required
def doctor_appointments(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    return render(request, "myapp/doctor/doctor_appointments.html")

@login_required
def doctor_patients(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    return render(request, "myapp/doctor/doctor_patients.html")

@login_required
def doctor_prescriptions(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    return render(request, "myapp/doctor/doctor_prescriptions.html")

@login_required
@login_required
def doctor_profile(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    
    try:
        doctor = request.user.doctor_profile
    except Exception:
        messages.error(request, "Doctor profile not found.")
        return redirect('login')
    
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            specialization = request.POST.get('specialization')
            
            # Validations
            if not first_name or not last_name:
                messages.error(request, 'First Name and Last Name are required.')
                return redirect('doctor_profile')
            
            # Update Doctor model fields
            doctor.first_name = first_name
            doctor.last_name = last_name
            
            # Update other fields
            if phone: doctor.phone = phone
            if email: doctor.email = email
            if specialization: doctor.specialization = specialization
            
            # Handle Image
            if 'profile_image' in request.FILES:
                doctor.profile_image = request.FILES['profile_image']
                
            doctor.save()
            
            # Sync Auth User fields
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            if email: user.email = email
            user.save()
                
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctor_profile')
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            print(f"ERROR SAVING DOCTOR: {e}")
    
    # Pre-split name for the template inputs
    name_parts = doctor.name.split(' ', 1)
    first_name = name_parts[0] if len(name_parts) > 0 else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    context = {
        'doctor': doctor,
        'first_name': first_name,
        'last_name': last_name
    }
    return render(request, "myapp/doctor/profile.html", context)

# ============ PATIENT VIEWS ============

@login_required
def patient_dashboard(request):
    if request.user.user_type != 'patient':
        return redirect('login')
    
    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        return redirect('login')
    
    # Get upcoming appointments
    upcoming_appointments = OPDAppointment.objects.filter(
        patient=patient,
        appointment_date__gte=timezone.now(),
        status='Pending'
    ).order_by('appointment_date')[:3]
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.objects.filter(
        patient=patient
    ).order_by('-created_at')[:3]
    
    # Get pending bills (Payment model doesn't have status field, so count all)
    pending_payments = Payment.objects.filter(
        patient=patient
    ).count()
    
    # Stats
    total_appointments = OPDAppointment.objects.filter(patient=patient).count()
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'recent_prescriptions': recent_prescriptions,
        'pending_payments': pending_payments,
        'total_appointments': total_appointments,
    }
    return render(request, "myapp/patient/dashboard.html", context)

@login_required
def patient_book_appointment(request):
    if request.user.user_type != 'patient':
        return redirect('login')
    
    patient = request.user.patient_profile
    departments = Department.objects.all()
    doctors = Doctor.objects.filter(availability_status='Available')
    
    if request.method == 'POST':
        department_id = request.POST.get('department')
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        
        try:
            from datetime import datetime
            # Combine date and time
            appointment_datetime_str = f"{appointment_date} {appointment_time}"
            appointment_datetime = timezone.make_aware(
                datetime.strptime(appointment_datetime_str, '%Y-%m-%d %H:%M')
            )
            
            # Create appointment
            OPDAppointment.objects.create(
                patient=patient,
                doctor_id=doctor_id,
                appointment_date=appointment_datetime,
                reason=reason,
                status='Pending',
                visit_type='New',
                fee=500,
                token_no=0
            )
            
            messages.success(request, 'Appointment booked successfully!')
            return redirect('patient_appointments')
            
        except Exception as e:
            messages.error(request, f'Error booking appointment: {str(e)}')
    
    context = {
        'patient': patient,
        'departments': departments,
        'doctors': doctors,
    }
    return render(request, "myapp/patient/book_appointment.html", context)

@login_required
def patient_appointments(request):
    if request.user.user_type != 'patient':
        return redirect('login')
    
    patient = request.user.patient_profile
    
    # Handle cancellation
    if request.method == 'POST':
        appt_id = request.POST.get('appointment_id')
        try:
            appointment = OPDAppointment.objects.get(id=appt_id, patient=patient)
            appointment.status = 'Cancelled'
            appointment.save()
            messages.success(request, 'Appointment cancelled successfully')
        except OPDAppointment.DoesNotExist:
            messages.error(request, 'Appointment not found')
        return redirect('patient_appointments')
    
    appointments = OPDAppointment.objects.filter(
        patient=patient
    ).order_by('-appointment_date')
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    return render(request, "myapp/patient/appointments.html", context)

@login_required
def patient_prescriptions(request):
    if request.user.user_type != 'patient':
        return redirect('login')
    
    patient = request.user.patient_profile
    prescriptions = Prescription.objects.filter(
        patient=patient
    ).order_by('-created_at')
    
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
    }
    return render(request, "myapp/patient/prescriptions.html", context)

@login_required
def download_prescription(request, id):
    if request.user.user_type != 'patient':
        return redirect('login')
    
    prescription = get_object_or_404(Prescription, id=id)
    # Ensure patient owns this prescription
    if prescription.patient != request.user.patient_profile:
        return redirect('patient_prescriptions')
        
    return render(request, "myapp/patient/download_prescription.html", {'prescription': prescription})

@login_required
def patient_bills(request):
    if request.user.user_type != 'patient':
        return redirect('login')
    
    patient = request.user.patient_profile
    
    # 1. Fetch Existing Payments
    payments = Payment.objects.filter(patient=patient).order_by('-payment_date')
    
    # 2. Generate Bills from OPD Appointments
    opd_appointments = OPDAppointment.objects.filter(patient=patient).order_by('-appointment_date')
    bill_items = []
    
    for appt in opd_appointments:
        # Check if already paid (simplistic check: look for payment with same amount ~approx time or description)
        # Real system would link Payment to Appointment via ForeignKey
        is_paid = False
        matching_payment = None
        
        # Simple matching logic: Check if any payment description contains "OPD" and "Doctor Name" or generic match
        # Ideally, we should add a OneToOne or ForeignKey to Payment, but for this existing schema:
        # We will assume if status is 'Completed' it *might* be paid, but let's rely on Payment table.
        # BETTER STRATEGY: Show "Pay Now" if no payment found for this amount on this day.
        
        # Checking if a payment exists for this amount and date (approx)
        for payment in payments:
            if payment.amount == appt.fee and payment.payment_date.date() == appt.appointment_date.date():
                is_paid = True
                matching_payment = payment
                break
        
        bill_items.append({
            'id': f"OPD-{appt.id}",
            'type': 'OPD',
            'date': appt.appointment_date,
            'description': f"Consultation - Dr. {appt.doctor.name if appt.doctor else 'Unknown'}",
            'amount': appt.fee,
            'status': 'Paid' if is_paid else 'Pending',
            'obj_id': appt.id,
            'payment_id': matching_payment.id if matching_payment else None
        })

    # 3. Generate Bills from IPD Admissions
    ipd_admissions = IPDAdmission.objects.filter(patient=patient).order_by('-admission_date')
    
    for admission in ipd_admissions:
        # Calculate Bill Amount
        if admission.discharge_date:
            days = (admission.discharge_date.date() - admission.admission_date.date()).days
        else:
            days = (timezone.now().date() - admission.admission_date.date()).days
            
        if days == 0: days = 1 # Minimum 1 day charge
        
        # Get Bed Charge
        daily_charge = 0
        if admission.bed:
             daily_charge = admission.bed.daily_charge
        
        total_amount = days * daily_charge
        
        # Check Payment Status
        is_paid = False
        matching_payment = None
        # Simplified check
        for payment in payments:
            # Heuristic match
            if payment.amount == total_amount and payment.description and "IPD" in payment.description:
                is_paid = True
                matching_payment = payment
                break
        
        bill_items.append({
            'id': f"IPD-{admission.id}",
            'type': 'IPD',
            'date': admission.admission_date,
            'description': f"Inpatient Care - {days} Days (Ward: {admission.ward_no})",
            'amount': total_amount,
            'status': 'Paid' if is_paid else 'Pending',
            'obj_id': admission.id,
            'payment_id': matching_payment.id if matching_payment else None
        })
    
    # Sort all items by date desc
    bill_items.sort(key=lambda x: x['date'], reverse=True)
    
    total_billed = sum(item['amount'] for item in bill_items)
    total_paid = sum(p.amount for p in payments)
    total_pending = sum(item['amount'] for item in bill_items if item['status'] == 'Pending')
    
    context = {
        'patient': patient,
        'bill_items': bill_items,
        'payments': payments,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
    }
    return render(request, "myapp/patient/bills.html", context)


@login_required
def download_receipt(request, payment_id):
    if request.user.user_type != 'patient':
        return redirect('login')
        
    payment = get_object_or_404(Payment, id=payment_id)
    # Ensure patient owns this payment
    if payment.patient != request.user.patient_profile:
        return redirect('patient_bills')

    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from io import BytesIO
    from num2words import num2words # You might need to install this or implement a helper, I'll use a simple fallback if not available

    # Fallback for num2words if not installed, but for now assuming we can't install new packages easily, I will omit or use a simple placeholder.
    # Ideally: pip install num2words
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30, title=f"Receipt #{payment.id}")
    elements = []
    styles = getSampleStyleSheet()

    # --- Header ---
    # Hospital Name and Logo (if available) -> Using Text for now
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#2E86C1'), alignment=TA_CENTER)
    address_style = ParagraphStyle('Address', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)
    
    elements.append(Paragraph("Sanjeevan Health Care", header_style))
    elements.append(Paragraph("123 Medical Plaza, Health City, Gujarat, India - 380001", address_style))
    elements.append(Paragraph("Phone: +91 1234567890 | Email: healthcaresanjeevani433@gmail.com", address_style))
    elements.append(Spacer(1, 20))
    
    # --- Title ---
    title_style = ParagraphStyle('Title', parent=styles['Heading2'], fontSize=16, alignment=TA_CENTER, textColor=colors.black, spaceAfter=20)
    elements.append(Paragraph("PAYMENT RECEIPT / TAX INVOICE", title_style))
    elements.append(Spacer(1, 10))

    # --- Customer and Invoice Details (Two Columns) ---
    # Left Column: Patient Details
    patient_info = [
        [Paragraph("<b>BILLED TO:</b>", styles['Normal'])],
        [Paragraph(f"<b>Name:</b> {payment.patient.name}", styles['Normal'])],
        [Paragraph(f"<b>Address:</b> {payment.patient.address or 'N/A'}", styles['Normal'])],
        [Paragraph(f"<b>Phone:</b> {payment.patient.phone}", styles['Normal'])],
        [Paragraph(f"<b>Email:</b> {payment.patient.email}", styles['Normal'])]
    ]
    
    # Right Column: Invoice Details
    invoice_info = [
        [Paragraph(f"<b>Receipt No:</b> #{payment.id:05d}", styles['Normal'])],
        [Paragraph(f"<b>Date:</b> {payment.payment_date.strftime('%d-%b-%Y')}", styles['Normal'])],
        [Paragraph(f"<b>Payment Mode:</b> {payment.payment_method}", styles['Normal'])],
        [Paragraph(f"<b>Transaction ID:</b> {payment.transaction_id}", styles['Normal'])],
        [Paragraph(f"<b>Status:</b> PAID", styles['Normal'])]
    ]

    info_table_data = [[Table(patient_info, colWidths=[2.5*inch]), Table(invoice_info, colWidths=[2.5*inch])]]
    info_table = Table(info_table_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # --- Items Table ---
    # Columns: Sl No, Description, Rate, Qty, Tax, Amount
    table_data = [
        ['Sr.', 'Description', 'Qty', 'Rate', 'Tax', 'Total']
    ]
    
    # Since Payment model doesn't have individual items linked directly in a granular way for this receipt generation (it's a lump sum usually),
    # we will use the description.
    # If we had a related 'PaymentItem' model, we would iterate it.
    # For now, treating the whole payment as one line item.
    
    table_data.append([
        '1',
        Paragraph(payment.description or "Medical Services / Hospital Bill", styles['Normal']),
        '1',
        f"{payment.amount}",
        '0.00',
        f"{payment.amount}"
    ])
    
    # Add empty rows to fill space if needed, or just totals
    
    # Totals Row
    table_data.append(['', '', '', '', 'Total', f"{payment.amount}"])

    col_widths = [0.5*inch, 3*inch, 0.6*inch, 1*inch, 0.8*inch, 1.2*inch]
    item_table = Table(table_data, colWidths=col_widths)
    
    item_table_style = TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey), # Grid for items
        
        # Content Alignment
        ('ALIGN', (1, 1), (1, -1), 'LEFT'), # Description Left
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'), # Amounts Right
        ('ALIGN', (-3, 1), (-3, -1), 'RIGHT'), # Rate Right
        
        # Total Row
        ('LINEABOVE', (4, -1), (-1, -1), 1, colors.black),
        ('FONTNAME', (4, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (4, -1), (-1, -1), colors.HexColor('#f2f2f2')),
    ])
    item_table.setStyle(item_table_style)
    elements.append(item_table)
    elements.append(Spacer(1, 20))

    # --- Total in Words (Static/Placeholder if library missing) ---
    amount_text = f"Rs. {payment.amount} ONLY"
    elements.append(Paragraph(f"<b>Total in words:</b> {amount_text}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # --- Bank Details (Static) ---
    bank_info = [
        [Paragraph("<b>Bank Details:</b>", styles['Normal'])],
        [Paragraph("Bank Name: HDFC Bank", styles['Normal'])],
        [Paragraph("Account No: 1234567890", styles['Normal'])],
        [Paragraph("IFSC Code: HDFC0001234", styles['Normal'])],
        [Paragraph("Branch: Health City", styles['Normal'])]
    ]
    
    # Signature box
    signature_image_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'images', 'signature.png')
    if os.path.exists(signature_image_path):
        signature = RLImage(signature_image_path, width=1.5*inch, height=0.5*inch)
        signature_data = [
            [signature],
            [Paragraph("<b>Authorized Signatory</b>", styles['Normal'])]
        ]
    else:
        signature_data = [
            [Spacer(1, 0.5*inch)],
            [Paragraph("<b>Authorized Signatory</b>", styles['Normal'])]
        ]
    
    footer_table_data = [[Table(bank_info), Table(signature_data, colWidths=[2.5*inch])]]
    footer_table = Table(footer_table_data, colWidths=[3.5*inch, 3.5*inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(footer_table)
    
    elements.append(Spacer(1, 30))
    
    # --- Terms ---
    # --- Terms ---
    elements.append(Paragraph("<b>Terms and Conditions:</b>", styles['Normal']))
    terms = [
        "1. This receipt is valid as proof of payment only.",
        "2. Consultation fees are non-refundable once the service is provided.",
        "3. Medicines, tests, and services once billed will not be taken back or exchanged.",
        "4. Any dispute shall be subject to Hospital Jurisdiction only.",
        "5. This is a computer-generated receipt and does not require a physical signature.",
        "6. For insurance claims, please submit this receipt along with the prescription/report.",
        "7. Hospital is not responsible for loss of this receipt after issuance."
    ]
    for term in terms:
        elements.append(Paragraph(term, styles['Normal']))

    # --- Paid Stamp Linker ---
    def add_stamp(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.green)
        canvas.setFillColor(colors.green)
        canvas.setLineWidth(3)
        
        # Translate to bottom right area usually, or near total
        # x, y coordinates - trial and error or calculated
        # A4 width ~ 595, height ~ 842. 
        # Let's put it roughly middle-right
        canvas.translate(400, 500) 
        canvas.rotate(30)
        
        # Draw Box
        canvas.roundRect(-50, -20, 100, 40, 4, stroke=1, fill=0)
        
        # Draw Text
        canvas.setFont('Helvetica-Bold', 20)
        canvas.drawCentredString(0, -7, "PAID")
        
        canvas.restoreState()

    # Build
    doc.build(elements, onFirstPage=add_stamp, onLaterPages=add_stamp)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    # Use 'inline' to view in browser, 'attachment' to force download
    response['Content-Disposition'] = f'inline; filename="Receipt_{payment.id}.pdf"'
    response.write(pdf)
    return response

@login_required
def make_payment(request):
    if request.user.user_type != 'patient':
        return redirect('login')
        
    if request.method == 'POST':
        item_id = request.POST.get('item_id') # e.g. "OPD-5"
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        
        # Record Payment
        Payment.objects.create(
            patient=request.user.patient_profile,
            amount=amount,
            payment_method='Online', # Defaulting to Online for this flow
            description=description
        )
        
        # If we had rigorous logic, we'd update the IPDAdmission or OPDAppointment status here
        # For now, the view logic above will detect the new Payment record and mark it Paid
        
        messages.success(request, 'Payment processed successfully!')
        return redirect('patient_bills')
    
    return redirect('patient_bills')

@login_required
def patient_profile(request):
    if request.user.user_type != 'patient':
        return redirect('login')
    
    patient = request.user.patient_profile
    
    if request.method == 'POST':
        # Handle profile update
        patient.name = request.POST.get('name')
        patient.age = request.POST.get('age')
        patient.blood_group = request.POST.get('blood_group')
        patient.phone = request.POST.get('phone')
        
        if request.POST.get('email'):
            patient.email = request.POST.get('email')
            request.user.email = request.POST.get('email')
            request.user.save()
        
        if request.FILES.get('profile_image'):
            patient.profile_image = request.FILES['profile_image']
        
        patient.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('patient_profile')
    
    context = {
        'patient': patient,
    }
    return render(request, "myapp/patient/profile.html", context)


# ============ DOCTOR VIEWS ============

@login_required
def doctor_dashboard(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
         return redirect('login') # Should not happen if user_type is doctor

    today = timezone.localdate()
    
    # Overview Stats
    today_opd = OPDAppointment.objects.filter(doctor=doctor, appointment_date__date=today).count()
    today_ipd = IPDAdmission.objects.filter(doctor=doctor, status='Admitted').count()
    pending_lab = LabReport.objects.filter(doctor=doctor, status='Pending').count()
    pending_discharge = IPDAdmission.objects.filter(doctor=doctor, is_discharge_requested=True, status='Admitted').count()
    
    # Next Appointment
    next_appt = OPDAppointment.objects.filter(
        doctor=doctor, 
        appointment_date__gte=timezone.now(),
        status='Pending'
    ).order_by('appointment_date').first()
    
    context = {
        'doctor': doctor,
        'today_opd': today_opd,
        'today_ipd': today_ipd,
        'pending_lab': pending_lab,
        'pending_discharge': pending_discharge,
        'next_appt': next_appt,
    }
    return render(request, 'myapp/doctor/dashboard.html', context)

@login_required
def doctor_opd_patients(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    doctor = request.user.doctor_profile
    today = timezone.localdate()
    
    # Show Today's Appointments (OPD)
    appointments = OPDAppointment.objects.filter(
        doctor=doctor, 
        appointment_date__date=today
    ).order_by('appointment_date')
    
    return render(request, 'myapp/doctor/opd_patients.html', {'appointments': appointments, 'doctor': doctor})

@login_required
def doctor_ipd_patients(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    doctor = request.user.doctor_profile
    
    # Admitted Patients
    admissions = IPDAdmission.objects.filter(doctor=doctor, status='Admitted').order_by('-admission_date')
    
    return render(request, 'myapp/doctor/ipd_patients.html', {'admissions': admissions, 'doctor': doctor})

@login_required
def doctor_appointments(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    doctor = request.user.doctor_profile
    
    # All appointments (future and past)
    appointments = OPDAppointment.objects.filter(doctor=doctor).order_by('-appointment_date')
    
    if request.method == 'POST':
        appt_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        
        try:
            appt = OPDAppointment.objects.get(id=appt_id, doctor=doctor)
            if action == 'complete':
                appt.status = 'Completed'
            elif action == 'cancel':
                appt.status = 'Cancelled'
            appt.save()
        except OPDAppointment.DoesNotExist:
            pass
            
        return redirect('doctor_appointments')
    
    return render(request, 'myapp/doctor/appointments.html', {'appointments': appointments, 'doctor': doctor})

@login_required
def doctor_prescriptions(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    doctor = request.user.doctor_profile
    
    prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-created_at')
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        appt_id = request.POST.get('appointment')
        diagnosis = request.POST.get('diagnosis')
        medicines = request.POST.get('medicines')
        advice = request.POST.get('advice')
        follow_up = request.POST.get('follow_up_date')
        
        Prescription.objects.create(
            doctor=doctor,
            patient_id=patient_id,
            appointment_id=appt_id if appt_id else None,
            diagnosis=diagnosis,
            medicines=medicines,
            advice=advice,
            follow_up_date=follow_up if follow_up else None
        )
        return redirect('doctor_prescriptions')

    patients = Patient.objects.all() # For dropdown
    patients = Patient.objects.all() # For dropdown
    return render(request, 'myapp/doctor/prescriptions.html', {'prescriptions': prescriptions, 'doctor': doctor, 'patients': patients})

@login_required
def prescription_print(request, id):
    if request.user.user_type != 'doctor':
        return redirect('login')
    
    prescription = get_object_or_404(Prescription, id=id)
    return render(request, 'myapp/doctor/print_prescription.html', {'p': prescription})

@login_required
def doctor_lab_reports(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    doctor = request.user.doctor_profile
    
    reports = LabReport.objects.filter(doctor=doctor).order_by('-requested_date')
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        test_name = request.POST.get('test_name')
        
        LabReport.objects.create(
            doctor=doctor,
            patient_id=patient_id,
            test_name=test_name,
            status='Pending'
        )
        return redirect('doctor_lab_reports')
        
    patients = Patient.objects.all()
    return render(request, 'myapp/doctor/lab_reports.html', {'reports': reports, 'doctor': doctor, 'patients': patients})

@login_required
def doctor_discharge_summary(request):
    if request.user.user_type != 'doctor':
        return redirect('login')
    doctor = request.user.doctor_profile
    
    summaries = DischargeSummary.objects.filter(doctor=doctor).order_by('-created_at')
    admitted_patients = IPDAdmission.objects.filter(doctor=doctor, status='Admitted')
    
    if request.method == 'POST':
        admission_id = request.POST.get('admission')
        diagnosis = request.POST.get('diagnosis')
        treatment = request.POST.get('treatment')
        advice = request.POST.get('advice')
        plan = request.POST.get('plan')
        
        try:
            admission = IPDAdmission.objects.get(id=admission_id)
            DischargeSummary.objects.create(
                admission=admission,
                patient=admission.patient,
                doctor=doctor,
                diagnosis=diagnosis,
                treatment_given=treatment,
                final_advice=advice,
                follow_up_plan=plan
            )
            
            # Optionally mark admission as discharge requested
            admission.is_discharge_requested = True
            admission.save()
            
        except Exception as e:
            print(e)
            
        return redirect('doctor_discharge_summary')
        
    return render(request, 'myapp/doctor/discharge_summary.html', {'summaries': summaries, 'admitted_patients': admitted_patients, 'doctor': doctor})

@login_required
def discharge_print(request, id):
    if request.user.user_type != 'doctor':
        return redirect('login')
    
    summary = get_object_or_404(DischargeSummary, id=id)
    return render(request, 'myapp/doctor/print_discharge.html', {'s': summary})



# Keeping doctor_patients as alias for opd or separate list if needed.
# For now we used opd_patients and ipd_patients.
def doctor_patients(request):
    return redirect('doctor_opd_patients')


# ============ PAYMENT VIEWS ============

@login_required
def initiate_payment(request):
    """Create Razorpay Order"""
    if request.method == "POST":
        try:
            amount_str = request.POST.get('amount')
            if not amount_str:
                 return JsonResponse({'error': 'Amount is required'}, status=400)
            
            amount = int(float(amount_str) * 100)  # Amount in paise
            
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            data = {
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            }
            order = client.order.create(data=data)
            
            return JsonResponse(order)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def payment_success(request):
    """Verify Payment Signature and Save Payment"""
    if request.method == "POST":
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            
            # Additional data passed from frontend
            patient_id = request.POST.get('patient_id') # Pass patient ID
            amount_paid = request.POST.get('amount')
            description = request.POST.get('description', 'Bill Payment')
            
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify Signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            # Verify signature (raises error if invalid)
            client.utility.verify_payment_signature(params_dict)
            
            # Save Payment to Database
            if patient_id:
                try:
                    patient = Patient.objects.get(id=patient_id)
                    Payment.objects.create(
                        patient=patient,
                        amount=amount_paid,
                        payment_method='Online',
                        description=description,
                        transaction_id=f"RZP-{razorpay_payment_id}",
                        razorpay_order_id=razorpay_order_id,
                        razorpay_payment_id=razorpay_payment_id,
                        razorpay_signature=razorpay_signature
                    )
                    return JsonResponse({'status': 'success'})
                except Patient.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Patient not found'})
            
            return JsonResponse({'status': 'error', 'message': 'Patient ID missing'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


# ============ AI CHAT MODULE ============

def ai_chat_response(message, user=None):
    message = message.lower()
    
    # --- Role Based Logic ---
    if user and user.is_authenticated:
        # 1. Receptionist Logic
        if user.user_type == 'staff' and hasattr(user, 'staff_profile') and user.staff_profile.role == 'Receptionist':
            # Patient Query
            patient_match = re.search(r'patient\s+(?:id\s+)?([a-z0-9]+)', message) or re.search(r'details\s+of\s+([a-z0-9]+)', message)
            if patient_match:
                query = patient_match.group(1)
                patients = Patient.objects.filter(Q(patient_id__iexact=query) | Q(name__icontains=query))
                if patients.exists():
                    p = patients.first()
                    return f"Patient Found: <b>{p.name}</b> (ID: {p.patient_id})<br>Age: {p.age}, Phone: {p.phone}<br>Address: {p.address}"
                else:
                    return f"No patient found matching '{query}'."
                    
            if 'availability' in message or 'check doctor' in message:
                return "You can check doctor availability on the <a href='/staff/receptionist/doctors/' class='text-primary fw-bold'>Doctor Schedule</a> page."

        # 2. Doctor Logic
        elif user.user_type == 'doctor':
             # Patient History / Meds
            patient_match = re.search(r'history\s+(?:of\s+)?(.+)', message) or re.search(r'stats\s+(?:for\s+)?(.+)', message)
            if patient_match:
                query = patient_match.group(1).strip()
                patients = Patient.objects.filter(name__icontains=query)
                if patients.exists():
                    p = patients.first()
                    # Mock history for now, or actual DB query
                    last_visit = OPDRegistration.objects.filter(patient=p, doctor=user.doctor_profile).last()
                    visit_info = f"Last visit: {last_visit.registration_date.strftime('%Y-%m-%d')}" if last_visit else "No recent visits with you."
                    return f"<b>{p.name}</b> ({p.age} {p.gender})<br>{visit_info}<br>Lab Reports: {LabReport.objects.filter(patient=p).count()}"
                else:
                    return f"No patient found named '{query}' in your list."

    # --- General / Public Logic ---
    
    # 1. Greetings
    if any(x in message for x in ['hi', 'hello', 'hey', 'start']):
        role_msg = ""
        if user and user.is_authenticated:
             role_msg = f" {user.first_name}"
        return f"Hello{role_msg}! I am your HMS Assistant. How can I help you today?"
        
    # 2. Appointment Booking
    if any(x in message for x in ['book', 'appointment', 'consult']):
        return "You can book an appointment easily. Please <a href='/register/patient/' class='text-primary fw-bold'>register here</a> if you are new, or <a href='/login/' class='text-primary fw-bold'>login</a> to your patient portal."
        
    # 3. Doctor Availability / specific specialty
    specialties = ['cardiologist', 'dentist', 'neurologist', 'physician', 'orthopedic', 'surgeon']
    for spec in specialties:
        if spec in message:
            doctors = Doctor.objects.filter(specialization__icontains=spec, availability_status='Available')
            if doctors.exists():
                doc_list = ", ".join([f"Dr. {d.name}" for d in doctors])
                return f"We have the following {spec}s available: {doc_list}. Would you like to book an appointment?"
            else:
                return f"I'm sorry, currently we don't have a {spec} available."
    
    if 'doctor' in message:
        return "We have specialized doctors in Cardiology, Orthopedics, Neurology, and General Medicine. Which specialist are you looking for?"
        
    # 4. Lab Reports
    if any(x in message for x in ['lab', 'report', 'test', 'result']):
        return "You can view your lab reports in the <a href='/login/' class='text-primary fw-bold'>Patient Portal</a>. If you have a physical receipt, please visit the Reception."
        
    # 5. Timing / Contact
    if any(x in message for x in ['time', 'open', 'hour']):
        return "Our hospital is open 24/7 for emergencies. OPD timings are 9:00 AM to 5:00 PM, Monday to Saturday."
        
    if any(x in message for x in ['contact', 'phone', 'call', 'address', 'location']):
        return "You can reach us at +91-9876543210 or visit us at Main Street, City Center. We are always here to help!"
        
    # 6. Thanks
    if any(x in message for x in ['thank', 'thanks', 'goodbye']):
        return "You're welcome! take care."

    # Fallback
    return "I'm not sure I understand. I can help with appointments, doctors, lab reports, and timings. Could you rephrase?"

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = data.get('message', '')
            session_id = data.get('session_id')
            
            # Manage Session
            if not session_id:
                session_id = str(uuid.uuid4())
                session = ChatSession.objects.create(session_id=session_id)
                if request.user.is_authenticated:
                    session.user = request.user
                    session.save()
            else:
                session, created = ChatSession.objects.get_or_create(session_id=session_id)
                if request.user.is_authenticated and not session.user:
                    session.user = request.user
                    session.save()
                
            # Log User Message
            ChatMessage.objects.create(
                session=session,
                sender='user',
                message=user_msg
            )
            
            # Generate Bot Response - Pass User
            bot_msg = ai_chat_response(user_msg, request.user)
            
            # Log Bot Message
            ChatMessage.objects.create(
                session=session,
                sender='bot',
                message=bot_msg
            )
            
            return JsonResponse({'status': 'success', 'response': bot_msg, 'session_id': session_id})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid Method'}, status=400)


# ============ BED MANAGEMENT VIEWS ============

@login_required
def bed_list(request):
    """List all beds (common for Admin and Receptionist)"""
    if request.user.user_type == 'admin':
        base_template = 'myapp/admin/base.html'
    elif request.user.user_type == 'staff' and request.user.staff_profile.role == 'Receptionist':
        base_template = 'myapp/staff/staff_base.html'
    else:
        return redirect('login')
    
    # Filtering
    ward_type = request.GET.get('ward_type')
    status = request.GET.get('status')
    
    beds = Bed.objects.all().order_by('ward_type', 'bed_number')
    
    if ward_type:
        beds = beds.filter(ward_type=ward_type)
    if status:
        beds = beds.filter(status=status)

    return render(request, "myapp/beds/bed_list.html", {
        'beds': beds,
        'base_template': base_template,
        'ward_types': Bed.WARD_CHOICES,
        'status_choices': Bed.STATUS_CHOICES,
        'selected_ward': ward_type,
        'selected_status': status
    })

@login_required
def bed_add(request):
    """Add new bed"""
    if request.user.user_type == 'admin':
        base_template = 'myapp/admin/base.html'
        redirect_url = 'bed_list'
    elif request.user.user_type == 'staff' and request.user.staff_profile.role == 'Receptionist':
        base_template = 'myapp/staff/staff_base.html'
        redirect_url = 'bed_list'
    else:
        return redirect('login')
    
    if request.method == 'POST':
        ward_type = request.POST.get('ward_type')
        bed_number = request.POST.get('bed_number')
        daily_charge = request.POST.get('daily_charge')
        status = request.POST.get('status')
        
        if Bed.objects.filter(bed_number=bed_number).exists():
             return render(request, "myapp/beds/bed_form.html", {
                'error': f'Bed number {bed_number} already exists.',
                'base_template': base_template
            })
        
        try:
            Bed.objects.create(
                ward_type=ward_type,
                bed_number=bed_number,
                daily_charge=daily_charge,
                status=status
            )
            messages.success(request, f'Bed {bed_number} added successfully!')
            return redirect(redirect_url)
        except Exception as e:
            return render(request, "myapp/beds/bed_form.html", {
                'error': f'Error adding bed: {str(e)}',
                'base_template': base_template
            })
            
    return render(request, "myapp/beds/bed_form.html", {'base_template': base_template})

@login_required
def bed_edit(request, id):
    """Edit bed details"""
    if request.user.user_type == 'admin':
        base_template = 'myapp/admin/base.html'
        redirect_url = 'bed_list'
    elif request.user.user_type == 'staff' and request.user.staff_profile.role == 'Receptionist':
        base_template = 'myapp/staff/staff_base.html'
        redirect_url = 'bed_list'
    else:
        return redirect('login')
    
    bed = get_object_or_404(Bed, id=id)
    
    if request.method == 'POST':
        bed.ward_type = request.POST.get('ward_type')
        bed.bed_number = request.POST.get('bed_number')
        bed.daily_charge = request.POST.get('daily_charge')
        bed.status = request.POST.get('status')
        
        try:
            bed.save()
            messages.success(request, f'Bed {bed.bed_number} updated successfully!')
            return redirect(redirect_url)
        except Exception as e:
             return render(request, "myapp/beds/bed_form.html", {
                'bed': bed,
                'error': f'Error updating bed: {str(e)}',
                'base_template': base_template
            })
    
    return render(request, "myapp/beds/bed_form.html", {
        'bed': bed,
        'base_template': base_template
    })

@login_required
def bed_delete(request, id):
    """Delete bed"""
    if request.user.user_type == 'admin':
        base_template = 'myapp/admin/base.html'
        redirect_url = 'bed_list'
    elif request.user.user_type == 'staff' and request.user.staff_profile.role == 'Receptionist':
        base_template = 'myapp/staff/staff_base.html'
        redirect_url = 'bed_list'
    else:
        return redirect('login')
    
    bed = get_object_or_404(Bed, id=id)
    
    if request.method == 'POST':
        bed_number = bed.bed_number
        bed.delete()
        messages.success(request, f'Bed {bed_number} deleted successfully!')
        return redirect(redirect_url)
    
    return render(request, "myapp/beds/bed_delete.html", {
        'bed': bed,
        'base_template': base_template
    })
