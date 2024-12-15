from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Ticket, TicketType
from .forms import EventForm, TicketTypeForm, CustomUserCreationForm, TicketPurchaseForm
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from .util import send_ticket_email



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['name']  # Save name as first name
            user.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'tickets/register.html', {'form': form})

@login_required
def event_list(request):
    events = Event.objects.filter(organizer=request.user)
    return render(request, 'tickets/event_list.html', {'events': events})  # Fixed path

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'tickets/create_event.html', {'form': form})  # Fixed path

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    # Fetch all ticket types for the event
    ticket_types = TicketType.objects.filter(event=event)
    
    # Fetch ticket counts grouped by type and status
    ticket_summary_raw = (
        Ticket.objects.filter(ticket_type__event=event)
        .values('ticket_type__id', 'ticket_type__name', 'status')
        .annotate(count=Count('id'))
    )
    
    # Initialize ticket summary with all ticket types and statuses
    statuses = ['Pending', 'Verified', 'Used']
    ticket_summary = {
        ticket_type.name: {status: 0 for status in statuses} 
        for ticket_type in ticket_types
    }
    
    # Populate ticket summary with actual counts
    for item in ticket_summary_raw:
        ticket_type_name = item['ticket_type__name']
        status = item['status']
        count = item['count']
        ticket_summary[ticket_type_name][status] = count

    return render(request, 'tickets/event_detail.html', {
        'event': event,
        'ticket_summary': ticket_summary,
    })

@login_required
def modify_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            if event.is_date_tbd:
                event.date = None  # Clear the date if TBD is selected
            event.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'tickets/modify_event.html', {'form': form, 'event': event})


@login_required
def manage_ticket_types(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    ticket_types = TicketType.objects.filter(event=event)
    
    if request.method == 'POST':
        form = TicketTypeForm(request.POST)
        if form.is_valid():
            ticket_type = form.save(commit=False)
            ticket_type.event = event
            ticket_type.save()
            return redirect('manage_ticket_types', event_id=event.id)
    else:
        form = TicketTypeForm()
    
    return render(request, 'tickets/manage_ticket_types.html', {
        'event': event,
        'ticket_types': ticket_types,
        'form': form,
    })
    
def event_landing(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ticket_types = TicketType.objects.filter(event=event)
    return render(request, 'tickets/event_landing.html', {
        'event': event,
        'ticket_types': ticket_types,
    })
    

@login_required
def modify_ticket_type(request, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, id=ticket_type_id, event__organizer=request.user)
    
    if request.method == 'POST':
        form = TicketTypeForm(request.POST, instance=ticket_type)
        if form.is_valid():
            form.save()
            return redirect('manage_ticket_types', event_id=ticket_type.event.id)
    else:
        form = TicketTypeForm(instance=ticket_type)
    
    return render(request, 'tickets/modify_ticket_type.html', {'form': form, 'ticket_type': ticket_type})

@login_required
def delete_ticket_type(request, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, id=ticket_type_id, event__organizer=request.user)
    event_id = ticket_type.event.id
    ticket_type.delete()
    return redirect('manage_ticket_types', event_id=event_id)

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    event.delete()
    return redirect('event_list')


def purchase_ticket(request, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, id=ticket_type_id)
    event = ticket_type.event

    payment_methods = {}
    if event.venmo_id:
        payment_methods['Venmo'] = f"Venmo: @{event.venmo_id}"
    if event.zelle_phone:
        payment_methods['Zelle'] = f"Zelle: {event.zelle_phone}"
    if event.bank_account_info:
        payment_methods['Bank Transfer'] = "Bank Transfer"

    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST, payment_methods=payment_methods)
        print(form.errors)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.ticket_type = ticket_type
            ticket.status = 'Pending'
            ticket.save()
            return redirect('purchase_confirmation', unique_id=ticket.unique_id)
    else:
        form = TicketPurchaseForm(payment_methods=payment_methods)

    return render(request, 'tickets/purchase_ticket.html', {
        'form': form,
        'event': event,
        'ticket_type': ticket_type,
    })



def purchase_confirmation(request, unique_id):
    ticket = get_object_or_404(Ticket, unique_id=unique_id)
    event = ticket.ticket_type.event
    
    # Build a list of available payment methods
    payment_methods = []
    if event.venmo_id:
        payment_methods.append(('Venmo', event.venmo_id))
    if event.zelle_phone:
        payment_methods.append(('Zelle', event.zelle_phone))
    if event.bank_account_info:
        payment_methods.append(('Bank', event.bank_account_info))
    
    return render(request, 'tickets/purchase_confirmation.html', {
        'ticket': ticket,
        'event': event,
        'payment_methods': payment_methods,
    })

@login_required
def manage_tickets(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    tickets = Ticket.objects.filter(ticket_type__event=event).order_by('-created_at')

    # Pagination
    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tickets/manage_tickets.html', {
        'event': event,
        'page_obj': page_obj,
    })

@require_POST
@login_required
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, ticket_type__event__organizer=request.user)
    new_status = request.POST.get('status')

    if new_status in ['Pending', 'Verified', 'Used']:
        ticket.status = new_status
        ticket.save()
        
        if new_status == 'Verified':
                # Send QR code email when ticket is verified
                send_ticket_email(ticket)

    # Redirect back to the ticket management page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def ticket_details(request, unique_id):
    ticket = get_object_or_404(Ticket, unique_id=unique_id, ticket_type__event__organizer=request.user)

    if request.method == 'POST' and 'update_status' in request.POST:
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Verified', 'Used']:
            ticket.status = new_status
            ticket.save()

            if new_status == 'Verified':
                # Send QR code email when ticket is verified
                send_ticket_email(ticket)

        return HttpResponseRedirect(request.path_info)  # Refresh the page

    return render(request, 'tickets/ticket_details.html', {'ticket': ticket})
