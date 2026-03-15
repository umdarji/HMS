from django.contrib import admin
from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Authentication URLs
    path('', views.unified_login_view, name="login"),
    path('login/', views.unified_login_view, name="unified_login"),
    path('verify-otp/', views.verify_otp_view, name="verify_otp"),
    path('resend-otp/', views.resend_otp_view, name="resend_otp"),
    path('register/patient/', views.patient_register_view, name="patient_register"),
    path('logout/', views.logout_view, name="logout"),
    
    # API URLs
    path('api/admin/dashboard-stats/', api_views.dashboard_stats_api, name="api_dashboard_stats"),
    path('api/admin/reports-stats/', api_views.reports_stats_api, name="api_reports_stats"),
    path('api/admin/reports/financial-pdf/', api_views.financial_report_pdf, name="financial_report_pdf"),
    path('api/admin/reports/patient-excel/', api_views.patient_records_excel, name="patient_records_excel"),
    path('api/admin/reports/staff-csv/', api_views.staff_performance_csv, name="staff_performance_csv"),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('admin/doctors/', views.admin_doctors, name="admin_doctors"),
    path('admin/doctors/add/', views.admin_add_doctor, name="admin_add_doctor"),
    path('admin/doctors/edit/<int:id>/', views.admin_edit_doctor, name="admin_edit_doctor"),
    path('admin/doctors/view/<int:id>/', views.admin_view_doctor, name="admin_view_doctor"),
    path('admin/doctors/delete/<int:id>/', views.admin_delete_doctor, name="admin_delete_doctor"),
    path('admin/doctors/pdf/', views.admin_doctors_pdf, name="admin_doctors_pdf"),
    path('admin/patients/', views.admin_patients, name="admin_patients"),
    path('admin/patients/add/', views.admin_add_patient, name="admin_add_patient"),
    path('admin/patients/view/<int:id>/', views.admin_view_patient, name="admin_view_patient"),
    path('admin/patients/delete/<int:id>/', views.admin_delete_patient, name="admin_delete_patient"),
    path('admin/patients/pdf/', views.admin_patients_pdf, name="admin_patients_pdf"),
    path('admin/appointments/', views.admin_appointments, name="admin_appointments"),
    path('admin/billing/', views.admin_billing, name="admin_billing"),
    path('admin/reports/', views.admin_reports, name="admin_reports"),
    path('admin/profile/', views.admin_profile, name="admin_profile"),

    
    # New Admin Modules
    path('admin/departments/', views.department_list, name="department_list"),
    path('admin/departments/add/', views.add_department, name="add_department"),
    path('admin/departments/edit/<int:id>/', views.edit_department, name="edit_department"),
    path('admin/departments/delete/<int:id>/', views.delete_department, name="delete_department"),
    
    path('admin/staff/', views.staff_list, name="staff_list"),
    path('admin/staff/add/', views.add_staff, name="add_staff"),
    path('admin/staff/edit/<int:id>/', views.edit_staff, name="edit_staff"),
    path('admin/staff/delete/<int:id>/', views.delete_staff, name="delete_staff"),



    path('admin/opd/', views.opd_list, name="opd_list"),
    path('admin/opd/add/', views.opd_add, name="opd_add"),
    path('admin/opd/edit/<int:id>/', views.opd_edit, name="opd_edit"),

    path('admin/ipd/', views.ipd_list, name="ipd_list"),
    path('admin/ipd/add/', views.ipd_add, name="ipd_add"),
    path('admin/ipd/discharge/<int:id>/', views.ipd_discharge, name="ipd_discharge"),

    path('admin/payments/', views.payment_list, name="payment_list"),
    path('admin/payments/add/', views.add_payment, name="add_payment"),
    
    path('admin/payments/add/', views.add_payment, name="add_payment"),
    
    # Staff URLs
    path('staff-dashboard/', views.staff_dashboard, name="staff_dashboard"),

    # Laboratory
    path('staff/laboratory/dashboard/', views.laboratory_dashboard, name='laboratory_dashboard'),
    path('staff/laboratory/upload/<int:id>/', views.laboratory_upload_report, name='laboratory_upload_report'),
    path('staff/laboratory/add/', views.laboratory_add_test, name='laboratory_add_test'),

    # Receptionist
    path('staff/receptionist/dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('staff/receptionist/patient/add/', views.receptionist_add_patient, name='receptionist_add_patient'),

    # AI Chat
    path('api/chat/', views.chat_api, name='chat_api'),
    path('staff/receptionist/appointments/', views.receptionist_appointments, name='receptionist_appointments'),
    path('staff/receptionist/profile/', views.receptionist_profile, name="receptionist_profile"),
    # OPD
    path('staff/receptionist/opd/register/', views.receptionist_opd_register, name='receptionist_opd_register'),
    path('staff/receptionist/opd/slip/<int:id>/', views.receptionist_opd_slip, name='receptionist_opd_slip'),
    path('staff/receptionist/opd/list/', views.receptionist_opd_list, name='receptionist_opd_list'),
    # IPD
    path('staff/receptionist/ipd/admit/', views.receptionist_ipd_admit, name='receptionist_ipd_admit'),
    path('staff/receptionist/ipd/list/', views.receptionist_ipd_list, name='receptionist_ipd_list'),
    path('staff/receptionist/ipd/discharge/<int:id>/', views.receptionist_discharge, name='receptionist_discharge'),
    path('staff/receptionist/ipd/discharge/finalize/<int:id>/', views.receptionist_finalize_discharge, name='receptionist_finalize_discharge'),
    
    # Appointments
    path('staff/receptionist/appointment/book/', views.receptionist_book_appt, name='receptionist_book_appt'),
    path('staff/receptionist/appointment/reschedule/<int:id>/', views.receptionist_reschedule_appt, name='receptionist_reschedule_appt'),
    path('staff/receptionist/appointment/cancel/<int:id>/', views.receptionist_cancel_appt, name='receptionist_cancel_appt'),
    
    # Schedule & Billing
    path('staff/receptionist/doctors/', views.receptionist_doctor_schedule, name='receptionist_doctor_schedule'),
    path('staff/receptionist/doctor/status/<int:id>/', views.receptionist_update_doctor_status, name='receptionist_update_doctor_status'),
    path('staff/receptionist/billing/', views.receptionist_billing_view, name='receptionist_billing_view'),
    path('staff/receptionist/profile/', views.receptionist_profile, name='receptionist_profile'),
    
    # Doctor URLs
    path('doctor/dashboard/', views.doctor_dashboard, name="doctor_dashboard"),
    path('doctor/opd-patients/', views.doctor_opd_patients, name="doctor_opd_patients"),
    path('doctor/ipd-patients/', views.doctor_ipd_patients, name="doctor_ipd_patients"),
    path('doctor/appointments/', views.doctor_appointments, name="doctor_appointments"),
    path('doctor/prescriptions/', views.doctor_prescriptions, name="doctor_prescriptions"),
    path('doctor/prescription/print/<int:id>/', views.prescription_print, name="prescription_print"),
    path('doctor/lab-reports/', views.doctor_lab_reports, name="doctor_lab_reports"),
    path('doctor/discharge-summary/', views.doctor_discharge_summary, name="doctor_discharge_summary"),
    path('doctor/discharge/print/<int:id>/', views.discharge_print, name="discharge_print"),
    path('doctor/profile/', views.doctor_profile, name="doctor_profile"),
    
    # Patient URLs
    path('patient/dashboard/', views.patient_dashboard, name="patient_dashboard"),
    path('patient/book-appointment/', views.patient_book_appointment, name="patient_book_appointment"),
    path('patient/appointments/', views.patient_appointments, name="patient_appointments"),
    path('patient/prescriptions/', views.patient_prescriptions, name="patient_prescriptions"),
    path('patient/prescriptions/download/<int:id>/', views.download_prescription, name="download_prescription"),
    path('patient/bills/', views.patient_bills, name="patient_bills"),
    path('patient/pay/', views.make_payment, name="make_payment"),
    path('patient/receipt/<int:payment_id>/', views.download_receipt, name="download_receipt"),
    path('patient/profile/', views.patient_profile, name="patient_profile"),
    
    # Payment URLs
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),

    # Bed Management
    path('beds/', views.bed_list, name='bed_list'),
    path('beds/add/', views.bed_add, name='bed_add'),
    path('beds/edit/<int:id>/', views.bed_edit, name='bed_edit'),
    path('beds/delete/<int:id>/', views.bed_delete, name='bed_delete'),
]
