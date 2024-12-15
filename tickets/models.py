from django.db import models
import uuid
from .util import CURRENCY_CHOICES, PAYMENT_METHOD_CHOICES
import qrcode
import base64
from django.conf import settings
from io import BytesIO

# Create your models here.

class Event(models.Model):
    organizer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_date_tbd = models.BooleanField(default=False)  # New field for TBD date
    date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255)
    venmo_id = models.CharField(max_length=255, blank=True, null=True)  # Optional Venmo ID
    zelle_phone = models.CharField(max_length=15, blank=True, null=True)  # Optional Zelle phone
    bank_account_info = models.TextField(blank=True, null=True)  # Optional Bank details
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=255)  # e.g., "General Admission", "VIP"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    quantity_available = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.event.name}"
    
class Ticket(models.Model):
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_identifier = models.CharField(max_length=255)  # Venmo ID, Zelle phone, or Bank details
    status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Used', 'Used'),
        ('Expired', 'Expired')
    ], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Secure ID field

    def __str__(self):
        return f"Ticket for {self.ticket_type.name} ({self.status})"
    
    def generate_qr_code_base64(self):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(f"{settings.SITE_URL}/tickets/{self.unique_id}/")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        return qr_base64