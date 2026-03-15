# Hospital Management System - Process Flows

This document outlines the operational workflows for all user roles within the system.

## 1. Authentication & Entry
*   **Unified Login**: All users (Admin, Doctor, Staff, Patient) log in via the main login page (`/login/`).
*   **OTP Verification**: Secure access via OTP sent to email/phone (`/verify-otp/`).
*   **Role-Based Redirection**:
    *   **Admin** -> `/admin/dashboard/`
    *   **Doctor** -> `/doctor/dashboard/`
    *   **Receptionist** -> `/staff/receptionist/dashboard/`
    *   **Patient** -> `/patient/dashboard/`

---

## 2. Admin Workflows
**Objective**: Full system oversight and management.

### User Management
*   **Doctors**:
    *   View all doctors (`/admin/doctors/`).
    *   Add new doctor (`/admin/doctors/add/`) with department and credentials.
    *   Edit/Delete doctor profiles.
*   **Patients**:
    *   View all patients (`/admin/patients/`).
    *   Add new patient (`/admin/patients/add/`).
    *   View patient details (`/admin/patients/view/<id>/`).
*   **Staff (Receptionists)**:
    *   Manage support staff (`/admin/staff/`).

### System Configuration
*   **Departments**: Create and manage hospital departments (`/admin/departments/`).
*   **Services**: Configure OPD/IPD settings.

### Financials & Reporting
*   **Billing Overview**: Monitor all incoming payments (`/admin/billing/`, `/admin/payments/`).
*   **Reports**: Access system-wide statistics (`/admin/reports/`) including financial PDFs and patient records.

---

## 3. Receptionist (Staff) Workflows
**Objective**: Front-desk operations, patient handling, and scheduling.

### Patient Management
*   **Registration**:
    *   **New Patient**: Register via `/staff/receptionist/patient/add/`.
    *   **OPD Registration**: Register patient for Out Patient Department (`/staff/receptionist/opd/register/`).
        *   *Output*: Generates an OPD Slip (`/staff/receptionist/opd/slip/<id>/`).
    *   **IPD Admission**: Admit patient to ward/bed (`/staff/receptionist/ipd/admit/`).

### Appointment Scheduling
*   **Booking**: Book appointments for registered patients (`/staff/receptionist/appointment/book/`).
*   **Management**: Reschedule or Cancel existing appointments (`/staff/receptionist/appointments/`).
*   **Doctor Availability**: View and update doctor status (Available/On Leave) (`/staff/receptionist/doctors/`).

### Billing & Discharge
*   **Billing**: Handle invoice generation and view payment status (`/staff/receptionist/billing/`).
*   **Discharge**: Process IPD patient discharge (`/staff/receptionist/ipd/discharge/<id>/`).

---

## 4. Doctor Workflows
**Objective**: Clinical care and patient treatment.

### Dashboard & Daily View
*   **Overview**: Quick stats on today's appointments and pending reviews (`/doctor/dashboard/`).
*   **Patient Lists**:
    *   **OPD**: View list of daily out-patients (`/doctor/opd-patients/`).
    *   **IPD**: View admitted in-patients (`/doctor/ipd-patients/`).

### Clinical Actions
*   **Consultation**: access patient records from appointment list (`/doctor/appointments/`).
*   **Prescribing**: Create digital prescriptions (`/doctor/prescriptions/`).
*   **Lab Reports**: Request or view uploaded lab results (`/doctor/lab-reports/`).
*   **Discharge Summaries**: Write medical summaries for discharged IPD patients (`/doctor/discharge-summary/`).

---

## 5. Patient Workflows
**Objective**: Self-service health management.

### Access & Booking
*   **Registration**: Self-register account (`/register/patient/`).
*   **Appointments**: Book slots with specific doctors (`/patient/book-appointment/`).

### Records & Payments
*   **Medical Records**:
    *   View/Download Prescriptions (`/patient/prescriptions/`).
    *   View Appointments History (`/patient/appointments/`).
*   **Financials**:
    *   View pending bills (`/patient/bills/`).
    *   Make online payments (`/patient/pay/`).
    *   Download payment receipts (`/patient/receipt/<id>/`).
