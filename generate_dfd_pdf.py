from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing, Circle, Rect, String, Line, Polygon
from reportlab.graphics import renderPDF

def draw_context_diagram():
    """
    Draws DFD Level 0 (Context Diagram)
    Central Process: Hospital Management System
    Entities: Admin, Doctor, Patient, Receptionist
    """
    d = Drawing(400, 300)
    
    # Center (System)
    cx, cy = 200, 150
    d.add(Circle(cx, cy, 50, fillColor=colors.lightblue, strokeColor=colors.black))
    d.add(String(cx, cy+5, "Smart", textAnchor='middle', fontSize=10, fontName='Helvetica-Bold'))
    d.add(String(cx, cy-5, "HMS", textAnchor='middle', fontSize=10, fontName='Helvetica-Bold'))
    
    # Entities
    entities = [
        {"name": "Admin", "x": 50, "y": 250},
        {"name": "Doctor", "x": 350, "y": 250},
        {"name": "Patient", "x": 350, "y": 50},
        {"name": "Receptionist", "x": 50, "y": 50},
    ]
    
    for ent in entities:
        # Draw Box
        w, h = 80, 40
        x, y = ent["x"] - w/2, ent["y"] - h/2
        d.add(Rect(x, y, w, h, fillColor=colors.lightgrey, strokeColor=colors.black))
        d.add(String(ent["x"], ent["y"]-2, ent["name"], textAnchor='middle', fontSize=9, fontName='Helvetica-Bold'))
        
        # Draw Line (Bi-directional arrows)
        # From Entity center to System center
        d.add(Line(ent["x"], ent["y"], cx, cy, strokeColor=colors.black))
        
        # Simple Arrow heads (decoration)
        mid_x = (ent["x"] + cx) / 2
        mid_y = (ent["y"] + cy) / 2
        # Just a dot to signify flow for simplicity in programmatic drawing
        d.add(Circle(mid_x, mid_y, 2, fillColor=colors.black))

    return d

def generate_dfd_pdf():
    pdf_path = "C:\\Users\\duman\\Desktop\\HMS\\DFD_Level_0_1_Smart_HMS.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, 
                                 textColor=colors.HexColor('#2c3e50'), spaceAfter=20, 
                                 alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    h1_style = ParagraphStyle('CustomH1', parent=styles['Heading2'], fontSize=16, 
                              textColor=colors.HexColor('#34495e'), spaceBefore=15, spaceAfter=10, 
                              fontName='Helvetica-Bold')

    # --- Title Page & Level 0 ---
    elements.append(Paragraph("Data Flow Diagrams (DFD)", title_style))
    elements.append(Paragraph("Smart Hospital Management System", title_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("DFD Level 0: Context Diagram", h1_style))
    elements.append(Spacer(1, 10))
    
    # Render Drawing
    drawing = draw_context_diagram()
    elements.append(drawing)
    elements.append(Spacer(1, 20))
    
    desc_text = """
    <b>Level 0 Overview:</b><br/>
    The Context Diagram represents the entire <b>Smart HMS</b> as a single process. 
    It interacts with four main external entities:<br/>
    1. <b>Admin</b>: Configures system, views reports.<br/>
    2. <b>Doctor</b>: Manages schedules, treatments, and prescriptions.<br/>
    3. <b>Receptionist</b>: Handles registrations, appointments, and billing.<br/>
    4. <b>Patient</b>: Requests services, views history.<br/>
    """
    elements.append(Paragraph(desc_text, styles['Normal']))
    
    elements.append(PageBreak())
    
    # --- Level 1 DFD ---
    elements.append(Paragraph("DFD Level 1: Functional Decomposition", h1_style))
    elements.append(Paragraph("This section breaks down the main system into its core functional processes, data stores, and flows.", styles['Normal']))
    elements.append(Spacer(1, 15))

    # Process Table Logic
    # P1: Auth
    # P2: Patient Mgmt
    # P3: Appointments
    # P4: IPD
    # P5: Clinical
    # P6: Billing
    
    processes = [
        {
            "id": "P1", "name": "Authentication & User Mgmt", 
            "inputs": "Login Creds, Registration Data",
            "outputs": "Session Token, User Profile, OTP",
            "stores": "D1 User Store, D1 OTP Store"
        },
        {
            "id": "P2", "name": "Patient Registration", 
            "inputs": "Patient Info (Name, Age, etc.)",
            "outputs": "Patient ID, Patient Record",
            "stores": "D1 User Store (Patient Profile)"
        },
        {
            "id": "P3", "name": "OPD Appointment Mgmt", 
            "inputs": "Date, Doctor Select, Reason",
            "outputs": "Token No, Appt Confirmation",
            "stores": "D2 Appointment Store, D7 Schedule Store"
        },
        {
            "id": "P4", "name": "IPD & Bed Management", 
            "inputs": "Admission Request, Bed Choice",
            "outputs": "Bed Allocation, IPD Record",
            "stores": "D3 Admission/Bed Store"
        },
        {
            "id": "P5", "name": "Clinical Management", 
            "inputs": "Diagnosis, Symptoms, Medicine",
            "outputs": "Prescription, Lab Report, Discharge Summary",
            "stores": "D5 Clinical Store"
        },
        {
            "id": "P6", "name": "Billing & Finance", 
            "inputs": "Fees, Bed Charges, Payment",
            "outputs": "Invoice, Receipt, Financial Report",
            "stores": "D4 Financial Store"
        },
        {
            "id": "P7", "name": "Resource Management", 
            "inputs": "Doc Availability, Dept Info",
            "outputs": "Exposed Schedule, Dept List",
            "stores": "D6 Resource Store, D7 Schedule Store"
        }
    ]
    
    # Create Table Data
    data = [['ID', 'Process Name', 'Input Flows', 'Output Flows', 'Data Stores']]
    for p in processes:
        data.append([
            p['id'], 
            Paragraph(p['name'], styles['Normal']),
            Paragraph(p['inputs'], styles['Normal']),
            Paragraph(p['outputs'], styles['Normal']),
            Paragraph(p['stores'], styles['Normal'])
        ])
        
    t = Table(data, colWidths=[0.5*inch, 1.5*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4ecf7')])
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Legend
    elements.append(Paragraph("<b>Legend:</b>", styles['Normal']))
    legend_data = [
        ["Process (P)", "Transforms input data to output data."],
        ["Data Store (D)", "Repositories where data is stored (Database Tables)."],
        ["Flows", "Movement of data between entities, processes, and stores."]
    ]
    t_legend = Table(legend_data, colWidths=[1.5*inch, 4*inch])
    t_legend.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(t_legend)

    doc.build(elements)
    print(f"PDF generated at: {pdf_path}")

if __name__ == "__main__":
    generate_dfd_pdf()
