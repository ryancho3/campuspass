CURRENCY_CHOICES = [
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('KRW', 'South Korean Won'),
    ('GBP', 'British Pound'),
    ('BTC', 'Bitcoin')]

PAYMENT_METHOD_CHOICES = [
    ('Venmo', 'Venmo'),
    ('Zelle', 'Zelle'),
    ('Bank Transfer', 'Bank Transfer'),
]

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from email.mime.image import MIMEImage
import base64

def send_ticket_email(ticket):
    # Get the base64-encoded QR code from your method
    qr_code_base64 = ticket.generate_qr_code_base64()
    qr_code_data = base64.b64decode(qr_code_base64)

    subject = f"Your Ticket for {ticket.ticket_type.event.name}"
    recipient_email = ticket.email

    # Render the template without embedding the base64 directly
    # Make sure your template uses `src="cid:qr_code"` instead of a data URI.
    html_content = render_to_string('tickets/ticket_email.html', {
        'ticket': ticket,
    })

    msg = EmailMultiAlternatives(
        subject=subject,
        body="",  # Plain text body if needed
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email]
    )

    # Attach the HTML content
    msg.attach_alternative(html_content, "text/html")

    # Attach the QR code image as a MIME attachment
    mime_image = MIMEImage(qr_code_data, _subtype="png")
    mime_image.add_header('Content-ID', '<qr_code>')
    mime_image.add_header('Content-Disposition', 'inline')
    msg.attach(mime_image)

    msg.send()
