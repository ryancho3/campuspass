from django.contrib import admin

# Register your models here.

from .models import Event, TicketType, Ticket

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizer', 'date', 'location')
    search_fields = ('name', 'organizer__username')

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'currency', 'quantity_available')
    search_fields = ('name', 'event__name')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'status', 'ticket_type')
    list_filter = ('status', 'ticket_type__event')
    search_fields = ('name', 'email', 'ticket_type__event__name')