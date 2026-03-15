
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Department

departments_data = [
    ("General Surgery", "Operations, wounds, hernia, appendix"),
    ("Orthopedics", "Bones, fractures, joints, spine"),
    ("Cardiology", "Heart problems"),
    ("Neurology", "Brain, nerves, paralysis, stroke"),
    ("Pulmonology", "Lungs, asthma, TB"),
    ("Gastroenterology", "Stomach, liver, digestion"),
    ("Nephrology", "Kidney diseases"),
    ("Urology", "Urine system, prostate"),
    ("Dermatology", "Skin, hair, nails"),
    ("ENT", "Ear, Nose, Throat"),
    ("Ophthalmology", "Eye care"),
    ("Pediatrics", "Child healthcare"),
    ("Gynecology & Obstetrics", "Women health, pregnancy, delivery"),
    ("Psychiatry", "Mental health"),
    ("Oncology", "Cancer treatment"),
]

for name, description in departments_data:
    dept, created = Department.objects.get_or_create(
        name=name, 
        defaults={'description': description}
    )
    if created:
        print(f"Created: {name}")
    else:
        print(f"Already exists: {name}")

print("Departments population complete.")
