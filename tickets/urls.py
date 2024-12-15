from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/modify/', views.modify_event, name='modify_event'),
    path('events/<int:event_id>/ticket-types/', views.manage_ticket_types, name='manage_ticket_types'),
    path('login/', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('', views.event_list, name='event_list'),  # Event list
    path('events/<int:event_id>/tickets/', views.event_landing, name='event_landing'),
    path('tickets/<int:ticket_type_id>/purchase/', views.purchase_ticket, name='purchase_ticket'),
    path('ticket-types/<int:ticket_type_id>/modify/', views.modify_ticket_type, name='modify_ticket_type'),
    path('ticket-types/<int:ticket_type_id>/delete/', views.delete_ticket_type, name='delete_ticket_type'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('tickets/<int:ticket_type_id>/purchase/', views.purchase_ticket, name='purchase_ticket'),
    path('tickets/purchase/confirmation/<uuid:unique_id>/', views.purchase_confirmation, name='purchase_confirmation'),
    path('events/<int:event_id>/tickets/manage/', views.manage_tickets, name='manage_tickets'),
    path('tickets/<int:ticket_id>/update-status/', views.update_ticket_status, name='update_ticket_status'),
    path('tickets/<uuid:unique_id>/', views.ticket_details, name='ticket_details'),
]