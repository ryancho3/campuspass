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

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_ticket_email(ticket):
    qr_code_base64 = ticket.generate_qr_code_base64()
    subject = f"Your Ticket for {ticket.ticket_type.event.name}"
    recipient_email = ticket.email

    # Render the email template
    message = render_to_string('tickets/ticket_email.html', {
        'ticket': ticket,
        'qr_code_base64': qr_code_base64,
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
        html_message=message,  # HTML email
    )
