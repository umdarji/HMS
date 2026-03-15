# Hospital Management System - Flowcharts

This document provides visual representations of the system's workflows for each user role.

## 1. Admin Workflow
Managing the overall hospital ecosystem: doctors, patients, staff, and finances.

```mermaid
graph TD
    A[Start: Login] --> B{Role: Admin?}
    B -- Yes --> C[Admin Dashboard]
    
    C --> D[Doctor Management]
    D --> D1[Add Doctor]
    D --> D2[Edit/Delete Doctor]
    D --> D3[View List]
    
    C --> E[Patient Management]
    E --> E1[View Patients]
    E --> E2[Add/Edit Patients]
    
    C --> F[Staff Management]
    F --> F1[Manage Receptionists]
    
    C --> G[Department Management]
    G --> G1[Add/Edit Departments]
    
    C --> H[Financials]
    H --> H1[View Billing]
    H --> H2[Track Payments]
    
    C --> I[Reports]
    I --> I1[Export Data]
```

## 2. Receptionist Workflow
Handling patient registration, appointments, and billing.

```mermaid
graph TD
    A[Start: Login] --> B{Role: Receptionist?}
    B -- Yes --> C[Receptionist Dashboard]
    
    C --> D[Patient Registration]
    D --> D1[Add New Patient]
    D1 --> D2{Type?}
    D2 -- OPD --> E[OPD Registration]
    E --> E1[Generate Slip]
    D2 -- IPD --> F[IPD Admission]
    F --> F1[Assign Ward/Bed]
    
    C --> G[Appointments]
    G --> G1[Book Appointment]
    G --> G2[Reschedule/Cancel]
    
    C --> H[Billing]
    H --> H1[Generate Invoice]
    H --> H2[Process Payment]
    
    C --> I[Doctor Schedule]
    I --> I1[Update Availability]
```

## 3. Doctor Workflow
Clinical operations: consultations, prescriptions, and patient care.

```mermaid
graph TD
    A[Start: Login] --> B{Role: Doctor?}
    B -- Yes --> C[Doctor Dashboard]
    
    C --> D[Appointments & Queue]
    D --> D1[View OPD Patients]
    D --> D2[View IPD Patients]
    
    D1 --> E[Consultation]
    E --> E1[View Medical History]
    E --> E2[Diagnose]
    E --> E3[Prescribe Medicine]
    
    D2 --> F[In-Patient Care]
    F --> F1[Daily Rounds]
    F --> F2[Discharge Summary]
    
    C --> G[Lab Reports]
    G --> G1[Request Tests]
    G --> G2[View Results]
```

## 4. Patient Workflow
Patient self-service portal.

```mermaid
graph TD
    A[Start] --> B{Registered?}
    B -- No --> C[Register Account]
    B -- Yes --> D[Login]
    
    C --> D
    
    D --> E[Patient Dashboard]
    
    E --> F[Appointments]
    F --> F1[Book New]
    F --> F2[View History]
    
    E --> G[Medical Records]
    G --> G1[View Prescriptions]
    G --> G2[Download Reports]
    
    E --> H[Financials]
    H --> H1[View Bills]
    H --> H2[Make Payment]
    H --> H3[Download Receipt]
```
