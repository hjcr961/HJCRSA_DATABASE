from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Service, Booking,BookingNumberCounter
from .forms import BookingForm
from .utils import send_booking_notification
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from .forms import ServiceForm
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.http import FileResponse
from decimal import Decimal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from django.contrib.staticfiles import finders
from reportlab.platypus import Table, TableStyle
from .forms import CustomUserCreationForm
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
import json
from datetime import datetime, time
from datetime import date
from .forms import StaffUserCreationForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail
import ssl
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from decimal import Decimal
from .models import Service, Booking, BookingNumberCounter, Room
from datetime import timedelta
import json





ssl._create_default_https_context = ssl._create_unverified_context

# Add at the top of the file with other imports















def home(request):
    return render(request, 'bookings/home.html')

def services(request):
    spa_services = Service.objects.filter(service_type='spa')
    lodge_services = Service.objects.filter(service_type='lodge')
    
    context = {
        'spa_services': spa_services,
        'lodge_services': lodge_services,
    }
    return render(request, 'bookings/services.html', context)


@login_required
def my_bookings(request):
    bookings = Booking.objects.all().order_by('-created_at', '-booking_date')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})



def is_owner(user):
    return user.is_staff

@user_passes_test(is_owner)
def manage_bookings(request):
    bookings = Booking.objects.filter(status='pending').select_related('customer').prefetch_related('services')
    return render(request, 'bookings/manage_bookings.html', {'bookings': bookings})


@user_passes_test(is_owner)
def approve_booking(request, booking_id):
    # Existing approval logic...
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'approved'
    booking.save()
    
    # Prepare email content
    subject = 'Your booking has been approved'
    message = render_to_string('bookings/booking_approved_email.html', {'booking': booking})
    recipient_email = booking.customer.email
    
    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])
    
    return redirect('bookings:manage_bookings')

@user_passes_test(is_owner)
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'rejected'
    booking.save()
    send_booking_notification(booking, 'rejected')
    return redirect('bookings:manage_bookings')

@user_passes_test(is_owner)
def owner_dashboard(request):
    today = timezone.now().date()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    approved_bookings = Booking.objects.filter(status='approved').count()
    canceled_bookings = Booking.objects.filter(status='canceled').count()
    today_bookings = Booking.objects.filter(booking_date=today).count()
    
    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'canceled_bookings': canceled_bookings,
        'today_bookings': today_bookings,
    }
    return render(request, 'bookings/owner_dashboard.html', context)


def get_bookings(request):
    bookings = Booking.objects.all()
    events = []
    for booking in bookings:
        # Create a title based on the services booked
        services_booked = ', '.join(service.name for service in booking.services.all())
        title = services_booked if services_booked else "No Services Booked"
        
        events.append({
            'title': title,
            'start': f"{booking.booking_date}T{booking.booking_time}",
            'url': reverse('bookings:booking_detail', args=[booking.id])
        })
    return JsonResponse(events, safe=False)


def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    services = booking.services.all()

    # Calculate correct price
    total_price = sum(Decimal(service.price) for service in services)
    
    # Update the database record with the correct price
    if booking.total_amount != total_price:
        booking.total_amount = total_price
        booking.save()
    
    # Determine if the booking is fully paid
    is_fully_paid = booking.payment_status == 'PAID'

    # Calculate deposit amount (e.g., 50% of total price) if not fully paid
    deposit_amount = Decimal('0') if is_fully_paid else total_price * Decimal('0.5')

    # Calculate remaining balance
    remaining_balance = Decimal('0') if is_fully_paid else total_price - deposit_amount

    # Calculate total outstanding amount
    total_outstanding = total_price - (total_price - remaining_balance)

    # Determine booking type based on services
    # If any service has 'lodge' or 'suite' in its name, it's a lodge booking
    is_lodge_booking = any(
        'lodge' in service.name.lower() or 
        'suite' in service.name.lower() or
        'room' in service.name.lower()
        for service in services
    )

    context = {
        'booking': booking,
        'total_price': total_price,
        'deposit_amount': deposit_amount,
        'remaining_balance': remaining_balance,
        'total_outstanding': total_outstanding,
        'number_of_people': booking.number_of_people,
        'is_lodge_booking': is_lodge_booking,  # Add this to determine label in template
    }
    return render(request, 'bookings/booking_detail_modal.html', context)


@login_required
def book_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.save()
            booking.services.add(service)
            messages.success(request, 'Your booking has been successfully created!')
            return redirect('bookings:my_bookings')  # Include the namespace here
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
                form = BookingForm(initial={
            'customer_name': request.user.first_name,
            'customer_surname': request.user.last_name,
        })
    return render(request, 'bookings/book_service.html', {'form': form, 'service': service})

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('booking_date', 'booking_time')
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def service_list(request):
    services = Service.objects.all()
    return render(request, 'bookings/service_list.html', {'services': services})

@login_required
@user_passes_test(is_staff)
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service created successfully!')
            return redirect('bookings:services')  # Redirects to services page
    else:
        form = ServiceForm()
    return render(request, 'bookings/service_form.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('bookings:services')  # Changed from 'service_list' to 'services'
    else:
        form = ServiceForm(instance=service)
    return render(request, 'bookings/service_form.html', {'form': form, 'editing': True})


@login_required
@user_passes_test(is_staff)
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service_list')
    return render(request, 'bookings/service_confirm_delete.html', {'service': service})

def get_available_rooms(service, booking_date, duration=1):
    available_rooms = []
    check_date = datetime.strptime(booking_date, '%Y-%m-%d').date()
    rooms = Room.objects.filter(room_type=service)
    
    for room in rooms:
        if room.is_available(check_date, duration):
            available_rooms.append(room)
            
    return available_rooms





@login_required
def create_booking(request):
    booking_type = request.GET.get('type')
    initial_data = {
        'booking_date': request.GET.get('booking_date')
    }

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            
            # Store services temporarily before saving
            selected_services = form.cleaned_data.get('services', [])
            booking._temp_services = selected_services
            
            number_of_people = form.cleaned_data['number_of_people']
            stay_duration = int(request.POST.get('stay_duration', 1))
            
            # Calculate total price
            total_price = sum(
            service.price * 
            (stay_duration if booking_type == 'lodge' else 1)
            for service in selected_services
        )
            booking.total_amount = total_price

            # Handle payment status
            if request.POST.get('payment_amount') == 'FULL':
                payment_type = request.POST.get('payment_type')
                if payment_type == 'EFT':
                    booking.status = 'pending'  # EFT payments should be pending until confirmed
                else:
                    booking.status = 'approved'  # Other payment methods can be approved immediately
                booking.payment_status = 'PAID'
                booking.deposit_paid = True
                booking.deposit_amount = total_price
                booking.outstanding_amount = 0
                booking.final_payment_method = request.POST.get('payment_type')
                booking.final_payment_date = timezone.now()
            elif request.POST.get('payment_amount') == 'DEPOSIT':
                booking.deposit_paid = True
                booking.deposit_amount = total_price * Decimal('0.5')
                booking.payment_status = 'DEPOSIT_PAID'
                booking.outstanding_amount = total_price * Decimal('0.5')
                booking.deposit_payment_method = request.POST.get('payment_type')
                booking.deposit_payment_date = timezone.now()
            else:
                booking.deposit_amount = 0
                booking.payment_status = 'UNPAID'
                booking.outstanding_amount = total_price

            # Generate booking number
            counter, _ = BookingNumberCounter.objects.get_or_create(booking_type=booking_type)
            counter.last_number += 1
            counter.save()
            prefix = 'SPA' if booking_type == 'spa' else 'LODGE'
            formatted_number = f"{counter.last_number:08d}"
            booking.booking_number = f"{prefix}-{formatted_number}"

            # Set end date
            booking.end_date = booking.booking_date + timedelta(days=stay_duration - 1)
            
            # Save booking first to get ID
            booking.save()
            
            # Now set the many-to-many relationship
            booking.services.set(selected_services)

            # Handle room assignment for lodge bookings
            if booking_type == 'lodge':
                for service in selected_services:
                    room_id = request.POST.get(f'room_{service.id}')
                    if room_id:
                        room = Room.objects.get(id=room_id)
                        if room.is_available(form.cleaned_data['booking_date'], stay_duration):
                            booking.room = room
                            booking.save()
                        else:
                            messages.error(request, f'Room {room.number} is no longer available for the selected dates.')
                            return redirect('bookings:create_booking')

            messages.success(request, 'Booking created successfully!')
            return redirect('bookings:my_bookings')
        else:
            messages.error(request, 'Please correct the errors in the form.')

    else:
        form = BookingForm(initial=initial_data)

    services = Service.objects.filter(service_type=booking_type)
    booking_date = request.GET.get('booking_date')
    
    context = {
        'form': form,
        'booking_type': booking_type,
        'services': services,
        'rooms': Room.objects.all(),
        'available_rooms': json.dumps({
        str(service.id): [
        {'id': room.id, 'number': room.number, 'description': getattr(room, 'description', '')}
        for room in get_available_rooms(service, booking_date)
        ]
        for service in services if service.service_type == 'lodge'
        })

    }
    return render(request, 'bookings/create_booking.html', context)


def mark_fully_paid(request, order_id):
    order = get_object_or_404(Booking, id=order_id)
    if request.method == 'POST':
        payment_method = request.POST.get('payment_type')
        # Update the order to mark it as fully paid
        order.outstanding_amount = 0
        order.status = 'approved'
        order.payment_status = 'PAID'
        order.final_payment_method = payment_method
        order.final_payment_date = timezone.now()
        order.processed_by = request.user
        order.save()
        
        messages.success(request, f'Payment of R{order.outstanding_amount} processed successfully via {payment_method}')
        return redirect('bookings:recon_report')

    return redirect('bookings:recon_report')













def create_booking_view(request):
    form = BookingForm(request.GET or None)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            # Handle successful booking creation
    return render(request, 'bookings/create_booking.html', {'form': form})






def is_staff(user):
    return user.is_staff


def generate_booking_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=18)
    
    elements = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomHeading1', parent=styles['Heading1'], fontSize=16, textColor=colors.darkblue, spaceAfter=12))
    styles.add(ParagraphStyle(name='CustomHeading2', parent=styles['Heading2'], fontSize=14, textColor=colors.darkblue, spaceAfter=6))
    
    logo_path = finders.find('images/logo.png')
    if logo_path:
        logo = Image(logo_path, width=2*inch, height=1*inch)
        elements.append(logo)
    else:
        elements.append(Paragraph("Logo not found", styles['Normal']))
    
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Booking Confirmation", styles['CustomHeading1']))
    
    # Customer Information Table
    customer_data = [
        ['Customer', f"{booking.customer_name} {booking.customer_surname}"],
        ['Booking Date', booking.booking_date],
        ['Time', booking.booking_time],
        ['Number of People', booking.number_of_people],
    ]
    customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("Services", styles['CustomHeading2']))
    
    # Services Table with per-person calculations
# Services Table with fixed pricing (not per-person)
    services_data = [['Service', 'Price', 'Total']]
    for service in booking.services.all():
        service_price = service.price
        # Don't multiply by number_of_people
        total_service_price = service_price
        services_data.append([
            service.name, 
            f"R{service_price:.2f}",
            f"R{total_service_price:.2f}"
        ])
    
    services_table = Table(services_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
    services_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(services_table)
    elements.append(Spacer(1, 12))
    
 # Calculate totals
    total_price = booking.total_amount
    if booking.payment_status == 'PAID':
        deposit_amount = total_price
        remaining_balance = Decimal('0')
    elif booking.deposit_paid:
        deposit_amount = booking.deposit_amount
        remaining_balance = booking.outstanding_amount
    else:
        deposit_amount = Decimal('0')
        remaining_balance = total_price

    
    # Summary Table
    summary_data = [
        ['Total Amount', f"R{total_price:.2f}"],
        ['Deposit Paid', f"R{deposit_amount:.2f}"],
        ['Remaining Balance', f"R{remaining_balance:.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f'booking_confirmation_{booking_id}.pdf')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')  # Replace 'home' with your home page URL name
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('bookings:booking_calendar')  # Redirects to booking calendar after login
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user, status='pending')
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            services = request.POST.getlist('services')
            total_price = sum(Service.objects.get(id=service_id).price for service_id in services)
            
            if form.cleaned_data['deposit_paid']:
                booking.deposit_amount = total_price * Decimal('0.5')
            
            booking.save()
            booking.services.set(services)
            messages.success(request, 'Booking updated successfully!')
            return redirect('bookings:my_bookings')
    else:
        form = BookingForm(instance=booking)
        
    # Filter services based on the booking's service type
    service_type = booking.services.first().service_type if booking.services.exists() else None
    services = Service.objects.filter(service_type=service_type)
    
    return render(request, 'bookings/create_booking.html', {
        'form': form,
        'editing': True,
        'booking': booking,
        'services': services,
        'booking_type': service_type
    })



def get_day_bookings(request):
    selected_date = request.GET.get('date')
    if not selected_date:
        # If no date is provided, default to today
        selected_date = timezone.now().date()
    else:
        # Parse the date string into a date object
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    # Get all bookings for the selected date
    bookings = Booking.objects.filter(
        booking_date=selected_date
    ).prefetch_related('services')

    # Generate time slots for the day (e.g., from 9 AM to 5 PM every hour)
    time_slots = []
    start_hour = 9
    end_hour = 17  # 5 PM
    for hour in range(start_hour, end_hour + 1):
        current_time = time(hour, 0)  # Creates time object for the hour

        # Get bookings for this time slot
        slot_bookings = bookings.filter(booking_time=current_time)
        booked_services = [{'id': service.id, 'name': service.name} for booking in slot_bookings for service in booking.services.all()]

        # Create the slot dictionary
        slot = {
            'hour': f"{hour:02d}",
            'minutes': "00",
            'booked_services': booked_services
        }

        time_slots.append(slot)

    # Get all available services
    available_services = Service.objects.all()

    context = {
        'selected_date': selected_date,
        'time_slots': time_slots,
        'services': available_services,
    }

    return render(request, 'bookings/day_bookings.html', context)

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

def staff_register(request):
    if request.method == 'POST':
        form = StaffUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('bookings:staff_dashboard')  # Redirect to staff dashboard
    else:
        form = StaffUserCreationForm()
    return render(request, 'registration/staff_register.html', {'form': form})

def staff_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('bookings:staff_dashboard')
            else:
                form.add_error(None, 'You are not authorized to access this area.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/staff_login.html', {'form': form})

@user_passes_test(is_staff_user)
def staff_dashboard(request):
    # Implement staff dashboard logic here
    return render(request, 'bookings/staff_dashboard.html')


def get_lodge_bookings(request):
    bookings = Booking.objects.filter(services__service_type='lodge')
    events = []
    for booking in bookings:
        title = f"{booking.customer_name}"
        if booking.room:
            title += f" - Room {booking.room.number}"
        events.append({
            'title': title,
            'start': f"{booking.booking_date.isoformat()}T{booking.booking_time}",  # Include time
            'url': reverse('bookings:booking_detail', args=[booking.id])
        })
    return JsonResponse(events, safe=False)

def get_spa_bookings(request):
    bookings = Booking.objects.filter(services__service_type='spa')
    events = []
    for booking in bookings:
        events.append({
            'title': f"{booking.customer_name}",
            'start': f"{booking.booking_date.isoformat()}T{booking.booking_time}",  # Include time
            'url': reverse('bookings:booking_detail', args=[booking.id])
        })
    return JsonResponse(events, safe=False)




def recon_report(request):
    # Filter orders with outstanding balance greater than zero
    outstanding_orders = Booking.objects.filter(outstanding_amount__gt=0)
    return render(request, 'bookings/recon_report.html', {'orders': outstanding_orders})


def mark_fully_paid(request, order_id):
    order = get_object_or_404(Booking, id=order_id)
    if request.method == 'POST':
        payment_method = request.POST.get('payment_type')  # This matches the hidden input name in the form
        order.outstanding_amount = 0
        order.status = 'approved'
        order.payment_status = 'PAID'
        order.final_payment_method = payment_method
        order.final_payment_date = timezone.now()
        order.processed_by = request.user
        order.save()
        
        messages.success(request, f'Payment of R{order.outstanding_amount} processed successfully via {payment_method}')
        return redirect('bookings:recon_report')

    
    

def end_of_day_report(request):
    selected_date = request.GET.get('date')  # Get the selected date from the request
    totals = []
    department_stats = None
    bookings = None
    payment_total = 0

    if selected_date:
        # Parse the selected date to ensure it's in the correct format
        selected_date = parse_date(selected_date)

        # Filter bookings by the selected date using the created_at field
        bookings = Booking.objects.filter(created_at__date=selected_date)
        
        # Get payment method totals
        totals = bookings.values('payment_type').annotate(
            total_amount=Sum('total_amount')
        ).order_by('payment_type')
        
        # Calculate total payments
        payment_total = bookings.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Get department statistics - determine type based on services
        # A booking is considered a 'lodge' booking if any of its services are of type 'lodge'
        # Otherwise, it's considered a 'spa' booking
        spa_bookings = []
        lodge_bookings = []
        
        for booking in bookings:
            service_types = set(booking.services.values_list('service_type', flat=True))
            if 'lodge' in service_types:
                lodge_bookings.append(booking)
            else:
                spa_bookings.append(booking)
        
        spa_total = sum(booking.total_amount for booking in spa_bookings)
        lodge_total = sum(booking.total_amount for booking in lodge_bookings)
        
        department_stats = {
            'spa': {
                'count': len(spa_bookings),
                'total': spa_total
            },
            'lodge': {
                'count': len(lodge_bookings),
                'total': lodge_total
            },
            'total': {
                'count': bookings.count(),
                'total': payment_total
            }
        }

    return render(request, 'bookings/end_of_day_report.html', {
        'totals': totals,
        'selected_date': selected_date,
        'department_stats': department_stats,
        'bookings': bookings,
        'payment_total': payment_total,
    })


    
@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    return redirect('bookings:login')

@login_required(login_url='bookings:login')
def booking_calendar(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access the booking calendar.")
    return render(request, 'bookings/booking_calendar.html')


def is_available(self, check_date, duration=1):
    from bookings.models import Booking
    
    if isinstance(check_date, str):
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    
    end_date = check_date + timedelta(days=duration-1)
    
    overlapping_bookings = Booking.objects.filter(
        room=self,
        booking_date__lte=end_date,
        end_date__gte=check_date,
        status__in=['pending', 'approved']
    ).exists()
    
    return not overlapping_bookings and self.status == 'available'


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Booking, Employee, BookingEmployeeAssignment, Service
from django.db.models import Q
from datetime import datetime, timedelta

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def spa_duties(request):
    # Get filter parameters
    date_filter = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    status_filter = request.GET.get('status', 'all')
    
    try:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except ValueError:
        filter_date = datetime.today().date()
    
    # Get all spa bookings for the selected date
    spa_bookings = Booking.objects.filter(
        services__service_type='spa',
        booking_date=filter_date
    ).distinct()
    
    if status_filter == 'assigned':
        spa_bookings = spa_bookings.filter(
            employee_assignments__isnull=False
        )
    elif status_filter == 'unassigned':
        spa_bookings = spa_bookings.filter(
            ~Q(id__in=BookingEmployeeAssignment.objects.values('booking_id'))
        )
    
    # Get all employees
    employees = Employee.objects.all().order_by('first_name')
    
    # Handle assignment form submission
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        employee_id = request.POST.get('employee_id')
        notes = request.POST.get('notes', '')
        
        if booking_id and employee_id:
            booking = get_object_or_404(Booking, id=booking_id)
            employee = get_object_or_404(Employee, id=employee_id)
            
            # Check if assignment already exists
            assignment, created = BookingEmployeeAssignment.objects.get_or_create(
                booking=booking,
                employee=employee,
                defaults={'notes': notes}
            )
            
            if not created:
                assignment.notes = notes
                assignment.save()
                messages.success(request, f"Updated assignment of {employee} to booking #{booking.booking_number}")
            else:
                messages.success(request, f"Assigned {employee} to booking #{booking.booking_number}")
            
            return redirect('bookings:spa_duties')
    
    # Get existing assignments for these bookings
    booking_assignments = {}
    for booking in spa_bookings:
        assignments = BookingEmployeeAssignment.objects.filter(booking=booking)
        if assignments.exists():
            booking_assignments[booking.id] = assignments
    
    # Date navigation
    prev_date = (filter_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (filter_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    context = {
        'spa_bookings': spa_bookings,
        'employees': employees,
        'booking_assignments': booking_assignments,
        'filter_date': filter_date,
        'status_filter': status_filter,
        'prev_date': prev_date,
        'next_date': next_date,
    }
    
    return render(request, 'bookings/spa_duties.html', context)

@login_required
@user_passes_test(is_admin)
def remove_employee_assignment(request, assignment_id):
    if request.method == 'POST':
        assignment = get_object_or_404(BookingEmployeeAssignment, id=assignment_id)
        booking_number = assignment.booking.booking_number
        employee_name = f"{assignment.employee.first_name} {assignment.employee.last_name}"
        
        assignment.delete()
        messages.success(request, f"Removed {employee_name} from booking #{booking_number}")
    
    return redirect('bookings:spa_duties')
