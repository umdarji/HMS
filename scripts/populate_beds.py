import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Bed

def populate_beds():
    ward_types = [
        ('General', '2500'),
        ('SemiPrivate', '4000'),
        ('Private', '6500'),
        ('Deluxe', '10000'),
        ('ICU', '15000'),
        ('CCU', '12000'),
        ('NICU', '10000'),
        ('PICU', '10000'),
        ('HDU', '8000'),
        ('Emergency', '3000'),
        ('Recovery', '3500'),
        ('PostOp', '4000'),
        ('Orthopedic', '5000'),
    ]

    print("Populating beds with 10 of each type...")
    
    total_count = 0
    for ward, price in ward_types:
        print(f"Processing {ward}...")
        created_count = 0
        
        # Determine prefix for bed numbers e.g., GEN, ICU
        prefix = ward[:3].upper()
        
        for i in range(1, 11): # Loop 1 to 10
            # Format bed number e.g., GEN-01, ICU-10
            bed_number = f"{prefix}-{str(i).zfill(2)}"
            
            # Check if this specific bed number exists
            if not Bed.objects.filter(bed_number=bed_number).exists():
                Bed.objects.create(
                    ward_type=ward,
                    bed_number=bed_number,
                    daily_charge=price,
                    status='Available'
                )
                print(f"  Created {bed_number}")
                created_count += 1
                total_count += 1
        
        if created_count == 0:
            print(f"  All 10 beds for {ward} already exist (or collisions prevented creation).")
            
    print(f"Done! Created {total_count} new beds.")

if __name__ == '__main__':
    populate_beds()
