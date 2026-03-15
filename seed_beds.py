import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Bed, Department

def seed_beds():
    print("Seeding Beds...")
    
    # Check if beds exist
    if Bed.objects.exists():
        print("Beds already exist. Skipping.")
        return

    beds_data = [
        {'ward': 'General Ward', 'prefix': 'GEN', 'count': 10, 'charge': 500},
        {'ward': 'Private Room', 'prefix': 'PVT', 'count': 5, 'charge': 2000},
        {'ward': 'ICU', 'prefix': 'ICU', 'count': 3, 'charge': 5000},
    ]

    for data in beds_data:
        for i in range(1, data['count'] + 1):
            bed_no = f"{data['prefix']}-{i:03d}"
            Bed.objects.create(
                ward_type=data['ward'],
                bed_number=bed_no,
                daily_charge=data['charge'],
                status='Available'
            )
            print(f"Created {bed_no}")

    print("Seeding Complete.")

if __name__ == '__main__':
    seed_beds()
