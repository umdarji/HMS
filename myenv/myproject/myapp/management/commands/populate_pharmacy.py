from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import Supplier, Medicine, PharmacyBill, PharmacyBillItem, Staff, CustomUser
import random
from datetime import timedelta, date

class Command(BaseCommand):
    help = 'Populates the database with dummy pharmacy data (Suppliers, Medicines, Bills)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting pharmacy data population...'))

        # 1. Create Suppliers
        suppliers = []
        company_suffixes = ['Pharma', 'Medical', 'Labs', 'Healthcare', 'BioTech', 'Life Sciences', 'Devices', 'Care', 'Solutions', 'Global']
        for i in range(10):
            name = f"Supplier {chr(65+i)} {random.choice(company_suffixes)}"
            supplier, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'contact_person': f"Manager {i+1}",
                    'phone': f"555-010{i}",
                    'email': f"contact@supplier{chr(97+i)}.com",
                    'address': f"{random.randint(100, 999)} Industrial Way, Tech City"
                }
            )
            suppliers.append(supplier)
        
        self.stdout.write(self.style.SUCCESS(f'Created/Found {len(suppliers)} Suppliers'))

        # 2. Create Medicines
        med_prefixes = ['Aspirin', 'Paracetamol', 'Ibuprofen', 'Amoxicillin', 'Metformin', 'Omeprazole', 'Lisinopril', 'Atorvastatin', 'Levothyroxine', 'Amlodipine']
        med_forms = ['Tablet', 'Syrup', 'Injection', 'Capsule', 'Cream', 'Drops']
        
        medicines_created = 0
        for i in range(100):
            name = f"{random.choice(med_prefixes)} {random.choice(med_forms)} {random.randint(10, 500)}mg"
            manufacturer = f"Manufacturer {chr(65 + random.randint(0, 5))}"
            
            # Randomize Expiry: 
            # 10% Expired (past 30 days)
            # 20% Expiring Soon (next 30 days)
            # 70% Valid (next 1-2 years)
            rand_val = random.random()
            today = timezone.now().date()
            if rand_val < 0.1:
                expiry_date = today - timedelta(days=random.randint(1, 30))
            elif rand_val < 0.3:
                expiry_date = today + timedelta(days=random.randint(1, 29))
            else:
                expiry_date = today + timedelta(days=random.randint(60, 730))
            
            # Randomize Stock
            # 10% Low stock (0-10)
            # 90% Normal stock (20-200)
            if random.random() < 0.1:
                stock = random.randint(0, 10)
            else:
                stock = random.randint(20, 200)

            Medicine.objects.create(
                name=name,
                manufacturer=manufacturer,
                supplier=random.choice(suppliers),
                batch_number=f"BN-{random.randint(10000, 99999)}",
                expiry_date=expiry_date,
                price=round(random.uniform(5.0, 150.0), 2),
                stock_quantity=stock,
                min_stock_alert=10,
                description="Synthetic test data"
            )
            medicines_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {medicines_created} Medicines'))

        # 3. Create Bills (Transactions) - Past 30 days
        # Need a pharmacist (or just use first staff found/admin)
        pharmacist = Staff.objects.filter(role='Pharmacist').first()
        if not pharmacist:
             # Fallback: create a dummy pharmacist if none exists, or just skip pharmacist link
             self.stdout.write(self.style.WARNING('No Pharmacist found. Bills will be created without pharmacist link.'))
        
        medicines = list(Medicine.objects.filter(stock_quantity__gt=0))
        bills_created = 0

        for i in range(50):
            bill_date = timezone.now() - timedelta(days=random.randint(0, 30))
            
            bill = PharmacyBill.objects.create(
                patient_name=f"Patient {i+1}",
                patient_phone=f"555-100{i}",
                pharmacist=pharmacist,
                payment_method=random.choice(['Cash', 'Card', 'UPI']),
                created_at=bill_date # Note: created_at auto_now_add=True might override this on save, need workaround or update
            )
            
            # Hack to set created_at for past dates (auto_now_add prevents direct set on create)
            bill.created_at = bill_date
            bill.save()

            # Add Items
            total_amount = 0
            num_items = random.randint(1, 4)
            chosen_meds = random.sample(medicines, num_items)
            
            for med in chosen_meds:
                qty = random.randint(1, 5)
                # Ensure we don't go negative on stock (though it's test data)
                if med.stock_quantity >= qty:
                    med.stock_quantity -= qty
                    med.save()
                    
                    item_total = med.price * qty
                    PharmacyBillItem.objects.create(
                        bill=bill,
                        medicine=med,
                        quantity=qty,
                        price=med.price,
                        total_price=item_total
                    )
                    total_amount += item_total
            
            bill.total_amount = total_amount
            bill.save()
            bills_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {bills_created} Pharmacy Bills'))
        self.stdout.write(self.style.SUCCESS('Data population complete!'))
