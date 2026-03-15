from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf():
    pdf_path = "C:\\Users\\duman\\Desktop\\HMS\\Data_Dictionary_Smart_HMS.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, 
                                 textColor=colors.HexColor('#2c3e50'), spaceAfter=20, 
                                 alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    h1_style = ParagraphStyle('CustomH1', parent=styles['Heading2'], fontSize=18, 
                              textColor=colors.HexColor('#34495e'), spaceBefore=20, spaceAfter=10, 
                              fontName='Helvetica-Bold')

    h2_style = ParagraphStyle('CustomH2', parent=styles['Heading3'], fontSize=14, 
                              textColor=colors.HexColor('#7f8c8d'), spaceBefore=15, spaceAfter=5, 
                              fontName='Helvetica-BoldOblique')
                              
    normal_style = styles['Normal']

    # --- Content Definitions ---
    
    # 1. Users & Authentication
    s1_data = {
        "title": "1. Users & Authentication",
        "tables": [
            {
                "name": "Table: myapp_customuser (Custom User Model)",
                "data": [
                    ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                    ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                    ['username', 'String', '150', 'Unique, Not Null', 'Username for login'],
                    ['password', 'String', '128', 'Not Null', 'Hashed password'],
                    ['user_type', 'String', '10', 'Choices', "Role: 'admin', 'doctor', 'patient', 'staff'"],
                    ['phone', 'String', '15', 'Nullable', 'Contact number'],
                    ['email', 'String', '254', 'Not Null', 'Email address'],
                    ['date_joined', 'DateTime', '-', 'Auto', 'Registration timestamp'],
                    ['is_active', 'Boolean', '-', 'Default=True', 'Account active status'],
                ]
            },
            {
                "name": "Table: myapp_otp",
                "data": [
                    ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                    ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                    ['user_id', 'Integer', '-', 'FK (CustomUser)', 'Linked User'],
                    ['otp_code', 'String', '6', 'Not Null', '6-digit OTP'],
                    ['created_at', 'DateTime', '-', 'Auto', 'Creation timestamp'],
                    ['expires_at', 'DateTime', '-', 'Not Null', 'Expiration timestamp'],
                    ['is_verified', 'Boolean', '-', 'Default=False', 'Verification status'],
                ]
            }
        ]
    }

    # 2. Profiles & Roles
    s2_data = {
        "title": "2. Profiles & Roles",
        "tables": [
            {
                "name": "Table: myapp_admin",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['user_id', 'Integer', '-', 'FK (CustomUser), Unique', 'Linked User Account'],
                     ['name', 'String', '200', 'Not Null', 'Full Name'],
                     ['profile_image', 'Image', '-', 'Nullable', 'Profile Picture path'],
                ]
            },
            {
                "name": "Table: myapp_doctor",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['user_id', 'Integer', '-', 'FK (CustomUser), Unique', 'Linked User Account'],
                     ['doctor_id', 'String', '10', 'Unique', 'Internal ID (e.g., DOC001)'],
                     ['name', 'String', '200', 'Not Null', 'Doctor Name'],
                     ['department_id', 'Integer', '-', 'FK (Department), Null', 'Specialized Department'],
                     ['specialization', 'String', '100', 'Not Null', 'Specific field (e.g., Cardiology)'],
                     ['availability_status', 'String', '20', 'Choices', "'Available', 'On Leave', 'Emergency'"],
                     ['phone', 'String', '15', 'Not Null', 'Contact Number'],
                     ['email', 'String', '254', 'Not Null', 'Contact Email'],
                ]
            },
            {
                "name": "Table: myapp_staff",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['user_id', 'Integer', '-', 'FK (CustomUser), Null', 'Optional link to User Account'],
                     ['staff_id', 'String', '10', 'Unique', 'Internal ID (e.g., STF001)'],
                     ['name', 'String', '200', 'Not Null', 'Staff Name'],
                     ['role', 'String', '50', 'Choices', "e.g., 'Receptionist'"],
                     ['department_id', 'Integer', '-', 'FK (Department)', 'Assigned Department'],
                     ['phone', 'String', '15', 'Not Null', 'Contact Number'],
                ]
            },
            {
                "name": "Table: myapp_patient",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['user_id', 'Integer', '-', 'FK (CustomUser), Unique', 'Linked User Account'],
                     ['patient_id', 'String', '10', 'Unique', 'Internal ID (e.g., PAT001)'],
                     ['name', 'String', '200', 'Not Null', 'Patient Name'],
                     ['age', 'Integer', '-', 'Not Null', 'Patient Age'],
                     ['gender', 'String', '10', 'Choices', "'Male', 'Female', 'Other'"],
                     ['blood_group', 'String', '5', 'Nullable', 'Blood Type'],
                     ['phone', 'String', '15', 'Not Null', 'Contact Number'],
                ]
            }
        ]
    }

    # 3. Hospital Logistics
    s3_data = {
        "title": "3. Hospital Logistics",
        "tables": [
             {
                "name": "Table: myapp_department",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['name', 'String', '100', 'Not Null', "e.g., 'Cardiology'"],
                     ['description', 'Text', '-', 'Nullable', 'Details about department'],
                ]
            },
            {
                "name": "Table: myapp_bed",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['bed_number', 'String', '10', 'Unique', "e.g., 'ICU-101'"],
                     ['ward_type', 'String', '20', 'Choices', "'General', 'ICU', 'Private'"],
                     ['status', 'String', '20', 'Default', "'Available', 'Occupied'"],
                     ['daily_charge', 'Decimal', '10,2', 'Not Null', 'Cost per day'],
                ]
            },
            {
                "name": "Table: myapp_doctorschedule",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['doctor_id', 'Integer', '-', 'FK (Doctor)', 'Linked Doctor'],
                     ['day_of_week', 'String', '10', 'Choices', "'Monday', 'Tuesday', etc."],
                     ['start_time', 'Time', '-', 'Not Null', 'Shift start'],
                     ['end_time', 'Time', '-', 'Not Null', 'Shift end'],
                ]
            }
        ]
    }

    # 4. Operational Data
    s4_data = {
         "title": "4. Operational Data",
        "tables": [
             {
                "name": "Table: myapp_opdappointment",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['patient_id', 'Integer', '-', 'FK (Patient)', 'Patient Appointed'],
                     ['doctor_id', 'Integer', '-', 'FK (Doctor)', 'Doctor Assigned'],
                     ['appointment_date', 'DateTime', '-', 'Not Null', 'Scheduled Date/Time'],
                     ['status', 'String', '20', 'Default', "'Pending', 'Completed'"],
                     ['visit_type', 'String', '20', 'Default', "'New' or 'Follow-up'"],
                     ['token_no', 'Integer', '-', 'Nullable', 'Queue Token Number'],
                     ['fee', 'Decimal', '10,2', 'Default', 'Consultation Fee'],
                ]
            },
            {
                "name": "Table: myapp_ipdadmission",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['patient_id', 'Integer', '-', 'FK (Patient)', 'Admitted Patient'],
                     ['doctor_id', 'Integer', '-', 'FK (Doctor)', 'Supervising Doctor'],
                     ['bed_id', 'Integer', '-', 'FK (Bed), Null', 'Allocated Bed'],
                     ['admission_date', 'DateTime', '-', 'Auto', 'Date of Admission'],
                     ['discharge_date', 'DateTime', '-', 'Nullable', 'Date of Discharge'],
                     ['ward_no', 'String', '50', 'Not Null', 'Ward Number'],
                     ['bed_no', 'String', '50', 'Not Null', 'Bed Number'],
                     ['status', 'String', '20', 'Default', "'Admitted', 'Discharged'"],
                ]
            },
            {
                "name": "Table: myapp_payment",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['patient_id', 'Integer', '-', 'FK (Patient)', 'Payer'],
                     ['amount', 'Decimal', '10,2', 'Not Null', 'Transaction Amount'],
                     ['payment_method', 'String', '20', 'Choices', "'Cash', 'Online'"],
                     ['description', 'Text', '-', 'Nullable', 'Reason for payment'],
                     ['transaction_id', 'String', '100', 'Nullable', 'External Ref ID'],
                ]
            }
        ]
    }

    # 5. Clinical Data
    s5_data = {
        "title": "5. Clinical Data",
        "tables": [
             {
                "name": "Table: myapp_prescription",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['patient_id', 'Integer', '-', 'FK (Patient)', 'Patient'],
                     ['doctor_id', 'Integer', '-', 'FK (Doctor)', 'Prescribing Doctor'],
                     ['appointment_id', 'Integer', '-', 'FK (OPDAppt)', 'Linked Appointment'],
                     ['medicines', 'Text', '-', 'Not Null', 'List of meds, dosage'],
                     ['diagnosis', 'Text', '-', 'Not Null', 'Medical logic'],
                ]
            },
            {
                "name": "Table: myapp_labreport",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['patient_id', 'Integer', '-', 'FK (Patient)', 'Patient'],
                     ['test_name', 'String', '200', 'Not Null', 'Test Name'],
                     ['report_file', 'File', '-', 'Nullable', 'Path to PDF/Image'],
                     ['status', 'String', '20', 'Default', "'Pending', 'Uploaded'"],
                ]
            },
            {
                "name": "Table: myapp_dischargesummary",
                "data": [
                     ['Attribute', 'Data Type', 'Field Size', 'Constraints', 'Description'],
                     ['id', 'Integer', '-', 'PK, Auto', 'Unique Record ID'],
                     ['admission_id', 'Integer', '-', 'FK (IPDAdmission)', 'Linked Admission'],
                     ['diagnosis', 'Text', '-', 'Not Null', 'Final Diagnosis'],
                     ['treatment_given', 'Text', '-', 'Not Null', 'Treatment during stay'],
                     ['final_advice', 'Text', '-', 'Not Null', 'Post-discharge care'],
                ]
            }
        ]
    }
    
    # --- Rendering ---
    
    # Title
    elements.append(Paragraph("Data Dictionary", title_style))
    elements.append(Paragraph("Smart Hospital Management System", title_style))
    elements.append(Spacer(1, 20))

    sections = [s1_data, s2_data, s3_data, s4_data, s5_data]

    for section in sections:
        elements.append(Paragraph(section['title'], h1_style))
        
        for table_info in section['tables']:
            elements.append(Paragraph(table_info['name'], h2_style))
            elements.append(Spacer(1, 5))
            
            # Create Table
            t = Table(table_info['data'], colWidths=[1.2*inch, 1.0*inch, 0.8*inch, 1.5*inch, 2.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.white),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ]))
            
            elements.append(t)
            elements.append(Spacer(1, 15))
        
        elements.append(PageBreak())

    # Build
    doc.build(elements)
    print(f"PDF generated at: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
