from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MainMembersForm, DependentsForm, TreasuryForm, TreasuryDepForm
from .models import MainMembers, Dependents, Treasury, TreasuryDep
from django.views.generic import ListView
from .models import ActivityLog
from django_filters.views import FilterView
from .filters import ActivityLogFilter
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import MainMembers
from django.db.models import Prefetch
from base64 import b64encode
from .models import MainMembers, MemberPictures
from PIL import Image
import io
from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages 
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .auth import CustomAuthBackend
from django.contrib.auth import authenticate, login
from datetime import datetime
from .models import MainMembers, Dependents
from .forms import MainMembersForm
from django.contrib.auth.decorators import permission_required
import json
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from .models import Picture
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.db.models import Sum
from django.db import transaction
from django.db import connection
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Elders, MainMembers
from django.http import JsonResponse
from base64 import b64encode
from django.db import connection
from datetime import datetime
from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse
import openpyxl

from django.db.models import Sum, Count, Q


def _get_fund_types_orm():
    """Get distinct fund types using ORM."""
    return Treasury.objects.values_list('fund', flat=True).distinct().order_by('fund')


def _build_fund_queryset(start_date, end_date, selected_fund_type):
    """Build queryset with filters using ORM."""
    queryset = Treasury.objects.all()

    if start_date:
        queryset = queryset.filter(payment_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(payment_date__lte=end_date)
    if selected_fund_type:
        queryset = queryset.filter(fund=selected_fund_type)

    return queryset


def _get_fund_report_data_orm(queryset):
    """Get aggregated fund data using ORM."""
    return (queryset
            .values('fund')
            .annotate(
        total_amount=Sum('amount'),
        num_payments=Count('idtreasury')
    )
            .order_by('fund'))


def _generate_excel_response(fund_data):
    """Generate Excel file response for fund report."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Fund Report"

    # Add headers
    ws.append(["Fund Type", "Total Amount", "Number of Payments"])

    # Add data rows
    for row in fund_data:
        ws.append([
            row["fund"],
            float(row["total_amount"] or 0),
            row["num_payments"]
        ])

    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=fund_report.xlsx'
    wb.save(response)
    return response


def fund_report(request):
    """Generate fund report with optional Excel export using Django ORM."""
    try:
        # Get fund types for dropdown
        fund_types = _get_fund_types_orm()

        # Extract filter parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        selected_fund_type = request.GET.get('fund_type', '')

        # Build queryset with filters
        queryset = _build_fund_queryset(start_date, end_date, selected_fund_type)

        # Get aggregated fund data
        fund_data = _get_fund_report_data_orm(queryset)

        # Handle Excel export
        if request.GET.get('export') == 'excel':
            return _generate_excel_response(fund_data)

        # Render HTML report
        return render(request, "main_app/fund_report.html", {
            "fund_data": fund_data,
            "start_date": start_date,
            "end_date": end_date,
            "fund_types": fund_types,
            "selected_fund_type": selected_fund_type,
        })

    except Exception as e:
        # Log the error and show user-friendly message
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in fund_report: {str(e)}")

        messages.error(request, "An error occurred while generating the report.")
        return render(request, "main_app/fund_report.html", {
            "fund_data": [],
            "start_date": start_date,
            "end_date": end_date,
            "fund_types": [],
            "selected_fund_type": selected_fund_type,
        })


import logging

logger = logging.getLogger(__name__)


def _validate_member_exists(branch_member_number):
    """Validate that a member exists with the given branch member number."""
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT Branch_Member_Number
                       FROM Main_Members
                       WHERE Branch_Member_Number = %s
                       """, [branch_member_number])
        return cursor.fetchone() is not None


def _process_uploaded_image(picture):
    """Process and compress uploaded image."""
    try:
        img = Image.open(picture)

        # Convert image mode if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Resize image
        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Compress image
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=10, optimize=True)
        compressed_image = buffer.getvalue()

        # Check size limit
        if len(compressed_image) > 65000:
            raise ValueError('Image is too large after compression')

        return compressed_image

    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        raise ValueError(f'Error processing image: {str(e)}')


def _picture_exists(branch_member_number):
    """Check if a picture already exists for the given member."""
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT COUNT(*)
                       FROM Member_Pictures
                       WHERE Branch_Member_Number = %s
                       """, [branch_member_number])
        return cursor.fetchone()[0] > 0


def _save_member_picture(branch_member_number, compressed_image):
    """Save or update member picture in database."""
    try:
        with connection.cursor() as cursor:
            if _picture_exists(branch_member_number):
                cursor.execute("""
                               UPDATE Member_Pictures
                               SET picture_data = %s,
                                   upload_date  = %s
                               WHERE Branch_Member_Number = %s
                               """, [compressed_image, timezone.now(), branch_member_number])
            else:
                cursor.execute("""
                               INSERT INTO Member_Pictures (Branch_Member_Number, picture_data, upload_date)
                               VALUES (%s, %s, %s)
                               """, [branch_member_number, compressed_image, timezone.now()])
    except Exception as e:
        logger.error(f"Database error saving picture for member {branch_member_number}: {str(e)}")
        raise


def _handle_picture_upload(request):
    """Handle the picture upload process."""
    picture = request.FILES['picture']
    branch_member_number = request.POST.get('branch_member_number')

    # Validate member exists
    if not _validate_member_exists(branch_member_number):
        messages.error(request, 'Invalid Branch Member Number. Please enter a valid member number.')
        return redirect('upload_picture')

    # Process image
    try:
        compressed_image = _process_uploaded_image(picture)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('upload_picture')

    # Save to database
    try:
        _save_member_picture(branch_member_number, compressed_image)
        messages.success(request, 'Picture uploaded successfully!')
        return redirect('member_list')
    except Exception as e:
        logger.error(f"Failed to save picture for member {branch_member_number}: {str(e)}")
        messages.error(request, 'Failed to save picture. Please try again.')
        return redirect('upload_picture')


@login_required
@require_http_methods(["GET", "POST"])
def upload_picture(request):
    """Handle member picture upload with validation and processing."""
    if request.method == 'POST':
        # Validate required data
        if 'picture' not in request.FILES:
            messages.error(request, 'Please select a picture to upload.')
            return redirect('upload_picture')

        if not request.POST.get('branch_member_number'):
            messages.error(request, 'Please provide a branch member number.')
            return redirect('upload_picture')

        # Handle the upload
        return _handle_picture_upload(request)

    # GET request - show upload form
    return render(request, 'main_app/upload_picture.html')




from django.db import transaction

def add_main_member(request):
    if request.method == 'POST':
        form = MainMembersForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Process dependents
                    dependent_first_names = request.POST.getlist('dependent_first_name[]')
                    dependent_last_names = request.POST.getlist('dependent_last_name[]')
                    number_of_dependants = calculate_number_of_dependants(dependent_first_names)
                    
                    # Get church title
                    church_title = request.POST.get('church_title', '')
                    
                    # Save main member
                    main_member = MainMembers.objects.create(
                        name=form.cleaned_data['name'],
                        surname=form.cleaned_data['surname'],
                        address=form.cleaned_data['address'],
                        gender=form.cleaned_data['gender'],
                        branch=form.cleaned_data['branch'],
                        phone_number=form.cleaned_data['phone_number'],
                        card_number=form.cleaned_data['card_number'],
                        church_title=church_title,
                        number_of_dependants=number_of_dependants,
                        registration_year=datetime.now().year
                    )
                    
                    # Save dependents
                    for first_name, last_name in zip(dependent_first_names, dependent_last_names):
                        if first_name.strip():
                            Dependents.objects.create(
                                name=first_name,
                                surname=last_name,
                                card_number=main_member.card_number
                            )
                
                return JsonResponse({'success': True})
            except Exception as e:
                import traceback
                print("Error saving member:", str(e))
                print(traceback.format_exc())
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = MainMembersForm()
        # Set default branch to JABULANI
        form.fields['branch'].initial = 'JABULANI'
        return render(request, 'main_app/add_main_member.html', {'form': form})




def handle_post_request(request):
    form = MainMembersForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors})

    # Process dependents and calculate their count
    dependent_first_names = request.POST.getlist('dependent_first_name[]')
    dependent_last_names = request.POST.getlist('dependent_last_name[]')
    number_of_dependants = calculate_number_of_dependants(dependent_first_names)

    # Get church_title from POST data
    church_title = request.POST.get('church_title', '')
    
    # Save the main member using the updated function
    main_member = save_main_member(form, number_of_dependants, church_title)

    # Save the dependents
    save_dependents(dependent_first_names, dependent_last_names, main_member.card_number)

    return JsonResponse({'success': True})


def handle_get_request(request):
    form = MainMembersForm()
    # Set default branch to JABULANI
    form.fields['branch'].initial = 'JABULANI'
    return render(request, 'main_app/add_main_member.html', {'form': form})

def calculate_number_of_dependants(dependent_first_names):
    return len([name for name in dependent_first_names if name.strip()])

def save_main_member(form, number_of_dependants, church_title=''):
    return MainMembers.objects.create(
        name=form.cleaned_data['name'],
        surname=form.cleaned_data['surname'],
        address=form.cleaned_data['address'],
        gender=form.cleaned_data['gender'],
        branch=form.cleaned_data['branch'],
        phone_number=form.cleaned_data['phone_number'],
        card_number=form.cleaned_data['card_number'],
        church_title=church_title,  # Add the church_title
        number_of_dependants=number_of_dependants,
        registration_year=datetime.now().year
    )

def save_dependents(dependent_first_names, dependent_last_names, card_number):
    for first_name, last_name in zip(dependent_first_names, dependent_last_names):
        if first_name.strip():
            Dependents.objects.create(
                name=first_name,
                surname=last_name,
                card_number=card_number
            )

def validate_card_number_add(request):
    card_number = request.GET.get('card_number', '')
    exists = not MainMembers.objects.filter(card_number=card_number).exists()
    return JsonResponse({'exists': exists})



def add_dependent(request):
    if request.method == 'POST':
        form = DependentsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dependent added successfully!')
            return redirect('dependent_list')
    else:
        form = DependentsForm()
    return render(request, 'main_app/add_dependent.html', {'form': form})



def add_treasury_dep(request):
    if request.method == 'POST':
        form = TreasuryDepForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treasury dependent record added successfully!')
            return redirect('treasury_dep_list')
    else:
        form = TreasuryDepForm()
    return render(request, 'main_app/add_treasury_dep.html', {'form': form})

def validate_card_number(request):
    card_number = request.GET.get('card_number', None)
    data = {
        'exists': MainMembers.objects.filter(card_number=card_number).exists()
    }
    return JsonResponse(data)

# List views



def member_list(request):
    # Fetch members ordered by surname and name
    members = MainMembers.objects.order_by('surname', 'name')
    
    # Fetch dependents
    dependents = Dependents.objects.order_by('surname', 'name')

    # Fetch pictures using raw SQL (since Member_Pictures is not a Django model)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Branch_Member_Number, picture_data 
            FROM Member_Pictures
        """)
        pictures = dict(cursor.fetchall())

        # Fetch dependent counts using raw SQL
        cursor.execute("""
            SELECT Card_Number, COUNT(*) as dependent_count
            FROM Dependents
            GROUP BY Card_Number
        """)
        dependent_counts = dict(cursor.fetchall())

    # Enrich member data
    for member in members:
        # Add picture URL
        picture_data = pictures.get(member.branch_member_number)
        member.picture_url = (
            f"data:image/jpeg;base64,{b64encode(picture_data).decode()}"
            if picture_data
            else '/static/default-profile.jpg'
        )

        # Add dependent count
        member.dependent_count = dependent_counts.get(member.card_number, 0)

    # Render the template
    return render(request, 'main_app/member_list.html', {
        'members': members,
        'dependents': dependents,  # Add dependents to the context
    })



def upload_member_picture(request, branch_member_number):
    if request.method == 'POST' and request.FILES.get('picture'):
        picture = request.FILES['picture']
        picture_data = picture.read()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Member_Pictures (Branch_Member_Number, picture_data)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE picture_data = VALUES(picture_data)
            """, [branch_member_number, picture_data])
            
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)





def dependent_list(request):
    dependents = Dependents.objects.all()
    return render(request, 'main_app/dependent_list.html', {'dependents': dependents})

@permission_required('main_app.view_treasury', raise_exception=True)
def treasury_list(request):
    treasury_records = Treasury.objects.all()
    return render(request, 'main_app/treasury_list.html', {'treasury_records': treasury_records})

@permission_required('main_app.view_treasurydep', raise_exception=True)
def treasury_dep_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT idTreasury_Dep, card_number, amount, fund, payment_date, Reciept_Number 
            FROM Treasury_Dep 
            ORDER BY payment_date DESC
        """)
        
        treasury_dep_records = [
            {
                'idTreasury_Dep': row[0],
                'card_number': row[1],
                'amount': row[2],
                'fund': row[3],
                'payment_date': row[4],
                'Reciept_Number': row[5]
            }
            for row in cursor.fetchall()
        ]
    
    return render(request, 'main_app/treasury_dep_list.html', {'treasury_dep_records': treasury_dep_records})

class ActivityLogView(ListView):
    model = ActivityLog
    template_name = 'main_app/activity_log.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        return ActivityLog.objects.select_related('user', 'content_type').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_activities'] = ActivityLog.objects.count()
        return context
    


class ActivityLogView(FilterView):
    model = ActivityLog
    template_name = 'main_app/activity_log.html'
    filterset_class = ActivityLogFilter
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_activities'] = ActivityLog.objects.count()
        return context



class MemberUpdateView(UpdateView):
    model = MainMembers
    template_name = 'main_app/member_form.html'
    fields = [
        'card_number',
        'name',
        'surname',
        'address',
        'phone_number',
        'branch',
        'gender',
        'registration_year',
        'number_of_dependants',
        'branch_member_number',
        'church_title' 
    ]
    success_url = reverse_lazy('member_list')



def member_payments(request, card_number):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT fund, amount, Fund_Date_Year, Fund_Date_Month, payment_date, receipt_number 
            FROM Treasury 
            WHERE idMain_Member = %s
            ORDER BY payment_date DESC
        """, [card_number])
        
        payments = [
            {
                'fund': row[0],
                'amount': row[1],
                'Fund_Date_Year': row[2],
                'Fund_Date_Month': row[3],
                'payment_date': row[4].strftime('%Y-%m-%d'),
                'receipt_number': row[5]
            }
            for row in cursor.fetchall()
        ]
        
    return JsonResponse(payments, safe=False)




def member_dependents(request, card_number):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT idDependents, name, surname 
            FROM Dependents 
            WHERE Card_Number = %s
            ORDER BY name
        """, [card_number])
        
        dependents = [
            {
                'idDependents': row[0],
                'name': row[1],
                'surname': row[2]
            }
            for row in cursor.fetchall()
        ]
        
    return JsonResponse(dependents, safe=False)



@permission_required('main_app.add_treasury', raise_exception=True)
def add_treasury(request):
    if request.method == 'POST':
        try:
            # Validate input data
            fund_types = request.POST.getlist('fund[]')
            fund_years = request.POST.getlist('fund_date_year[]')
            amounts = request.POST.getlist('amount[]')
            receipt_numbers = request.POST.getlist('receipt_number[]')
            idmain_member = request.POST.get('idmain_member')
            payment_date = request.POST.get('payment_date')
            fund_months = request.POST.getlist('fund_date_month[]')

            # Comprehensive input validation
            if not all([fund_types, fund_years, amounts, receipt_numbers, idmain_member,
                        payment_date, fund_months]):
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required'
                }, status=400)

            # Validate list lengths match
            if not (len(fund_types) == len(fund_years) ==
                    len(amounts) == len(fund_months) == len(receipt_numbers)):
                return JsonResponse({
                    'success': False,
                    'error': 'Mismatched input lengths'
                }, status=400)

            # Prepare treasury objects for bulk creation
            treasury_objects = []
            for i in range(len(fund_types)):
                try:
                    # Robust parsing and conversion
                    years = json.loads(fund_years[i])
                    amount = float(amounts[i])
                    receipt_number = int(receipt_numbers[i])
                except (ValueError, json.JSONDecodeError) as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'Invalid data at index {i}: {str(e)}'
                    }, status=400)

                # Create treasury objects for each year
                treasury_objects.extend([
                    Treasury(
                        idmain_member=idmain_member,
                        fund=fund_types[i],
                        amount=amount,
                        fund_date_year=int(year),
                        fund_date_month=fund_months[i],
                        payment_date=payment_date,
                        receipt_number=receipt_number
                    ) for year in years
                ])

            # Bulk create with error handling
            if treasury_objects:
                Treasury.objects.bulk_create(treasury_objects)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No treasury entries to create'
                }, status=400)

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('treasury_list')
            })

        except Exception as e:
            # Catch-all error handling
            return JsonResponse({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }, status=500)

    # GET request handling remains identical
    form = TreasuryForm()
    current_year = datetime.now().year
    years = range(current_year - 5, current_year + 3)

    return render(request, 'main_app/add_treasury.html', {
        'form': form,
        'years': years
    })




@permission_required('main_app.add_treasurydep', raise_exception=True)
def add_treasury_dep(request):
    if request.method == 'POST':
        form = TreasuryDepForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treasury dependent record added successfully!')
            return redirect('treasury_dep_list')
    else:
        form = TreasuryDepForm()
    return render(request, 'main_app/add_treasury_dep.html', {'form': form})


def validate_card_number(request):
    card_number = request.GET.get('card_number', '')
    
    if not card_number:
        return JsonResponse({'exists': False, 'message': 'Please enter a card number'})
    
    try:
        card_number = int(card_number)
        exists = MainMembers.objects.filter(card_number=card_number).exists()
        return JsonResponse({'exists': exists})
    except ValueError:
        return JsonResponse({'exists': False, 'message': 'Please enter a valid number'})


def validate_card_number_add(request):
    card_number = request.GET.get('card_number', '')
    exists = not MainMembers.objects.filter(card_number=card_number).exists()
    return JsonResponse({'exists': exists})


def dependent_payments(request, dependent_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT fund, amount, Fund_Date_Year, Fund_Date_Month, payment_date, Reciept_Number 
            FROM Treasury_Dep 
            WHERE Dependent_ID = %s
            ORDER BY payment_date DESC
        """, [dependent_id])
        
        payments = [
            {
                'fund': row[0],
                'amount': row[1],
                'Fund_Date_Year': row[2],
                'Fund_Date_Month': row[3],
                'payment_date': row[4].strftime('%Y-%m-%d'),
                'reciept_number': row[5]
            }
            for row in cursor.fetchall()
        ]
    
    return JsonResponse(payments, safe=False)




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.is_active:
                messages.add_message(request, messages.ERROR, 'Your account is awaiting administrator approval.')
                return render(request, 'registration/login.html')
            
            login(request, user)
            
            # Log the login action
            from .utils import log_user_action
            try:
                log_user_action(
                    user_email=user.email,
                    action='login',
                    details=f"User {user.username} logged in"
                )
                print("Log entry created successfully.")
            except Exception as e:
                print(f"Failed to log action: {e}")
            
            return redirect('main_app/home.html')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid username or password')
            return render(request, 'registration/login.html')
    
    return render(request, 'registration/login.html')






@login_required
def home_view(request):
    # Count total members
    total_members = MainMembers.objects.count()
    
    # Count total dependents
    total_dependents = Dependents.objects.count()

    # Calculate total value and count of "Annual" payments for the current year
    current_year = datetime.now().year
    annual_payments = Treasury.objects.filter(fund='Annual', fund_date_year=current_year)
    total_annual_value = annual_payments.aggregate(Sum('amount'))['amount__sum'] or 0
    total_annual_count = annual_payments.count()
    
    # Pass the data to the template
    context = {
        'total_members': total_members,
        'total_dependents': total_dependents,
        'total_annual_value': total_annual_value,
        'total_annual_count': total_annual_count,
        'current_year': current_year,  # Add this line
    }
    
    return render(request, 'main_app/home.html', context)

@login_required
def get_dependent_payments(request, card_number):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                d.name,
                d.surname,
                td.Fund,
                td.Amount,
                td.Fund_Date_Year,
                td.Reciept_Number,
                td.Payment_Date
            FROM Treasury_Dep td
            JOIN Dependents d ON td.Dependent_ID = d.idDependents
            WHERE td.Card_Number = %s
            ORDER BY td.Payment_Date DESC
        """, [card_number])
        
        columns = [col[0] for col in cursor.description]
        payments = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    return JsonResponse(payments, safe=False)

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'registration/signup.html')
        
        try:
            # Create user with is_active set to False
            user = User.objects.create_user(
                username=email, 
                email=email, 
                password=password,
                first_name=name,
                last_name=surname,
                is_active=False  # Set user to inactive by default
            )
            
            # Add success message and redirect to login
            messages.success(request, 'Account created. Awaiting administrator approval.')
            return redirect('login')
        
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'registration/signup.html')
    
    return render(request, 'registration/signup.html')

def get_gender_distribution(request):
    gender_data = MainMembers.objects.values('gender').annotate(
        count=Count('pk')  # Use 'pk' instead of 'id'
    ).order_by('gender')
    
    data = {
        'labels': [entry['gender'] for entry in gender_data],
        'counts': [entry['count'] for entry in gender_data]
    }
    
    return JsonResponse(data)



def log_user_action(user_email, action, details=None):
    """
    Log user actions to the user_activity_log table.
    
    Args:
        user_email (str): Email of the user performing the action
        action (str): Description of the action (e.g., 'login', 'add_member', 'edit_treasury')
        details (str, optional): Additional details about the action
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO user_activity_log (user_email, action, details, timestamp)
            VALUES (%s, %s, %s, %s)
        """, [user_email, action, details, timezone.now()])


@login_required
def view_action_logs(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, timestamp, user_email, action, details
            FROM user_actions
            ORDER BY timestamp DESC
            LIMIT 1000
        """)
        
        columns = [col[0] for col in cursor.description]
        logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'main_app/action_logs.html', {'logs': logs})


@login_required
def view_action_logs(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, timestamp, user_email, action, details
            FROM user_activity_log
            ORDER BY timestamp DESC
            LIMIT 1000
        """)
        
        columns = [col[0] for col in cursor.description]
        logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'main_app/action_logs.html', {'logs': logs})





@login_required
def barcode_list(request):
    """
    Display a list of all generated barcodes with member details
    """
    # Get all barcode entries with their related member details
    # The Elders model has a OneToOneField to MainMembers, so we can access
    # the MainMembers fields directly through the relationship
    barcodes = Elders.objects.select_related('branch_member_number').all()
    
    return render(request, 'main_app/barcode_list.html', {
        'barcodes': barcodes,
        'title': 'Barcode List',
    })

@login_required
def barcode_detail(request, barcode_id):
    """
    Display details for a specific barcode
    """
    barcode = Elders.objects.select_related('branch_member_number').get(id=barcode_id)
    
    return render(request, 'main_app/barcode_detail.html', {
        'barcode': barcode,
        'title': f'Barcode: {barcode.barcode_value}',
    })



@login_required
def barcode_scanner(request):
    """
    Provide an interface for scanning barcodes using a camera or physical scanner
    """
    return render(request, 'main_app/barcode_scanner.html', {
        'title': 'Barcode Scanner',
    })

@login_required
def barcode_lookup(request):
    """
    API endpoint to look up a barcode value and return member details
    """
    barcode_value = request.GET.get('barcode', '')
    
    if not barcode_value:
        return JsonResponse({'error': 'No barcode provided'}, status=400)
    
    try:
        # Look up the barcode in the database
        barcode = Elders.objects.select_related('branch_member_number').get(barcode_value=barcode_value)
        
        # Return member details as JSON
        return JsonResponse({
            'success': True,
            'member': {
                'id': barcode.id,
                'title': barcode.title,
                'name': barcode.branch_member_number.name,
                'surname': barcode.branch_member_number.surname,
                'branch_member_number': barcode.branch_member_number.branch_member_number,
                'branch': barcode.branch_member_number.branch,
                'status': barcode.status,
                'issue_date': barcode.issue_date.strftime('%Y-%m-%d'),
                'expiry_date': barcode.expiry_date.strftime('%Y-%m-%d'),
                'detail_url': reverse('barcode_detail', args=[barcode.id]),
            }
        })
    except Elders.DoesNotExist:
        return JsonResponse({'error': 'Barcode not found'}, status=404)

def member_details_api(request, card_number):
    try:
        # Use raw SQL to match the rest of your codebase
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT mm.card_number, mm.name, mm.surname, mm.branch, mm.gender, 
                       mm.phone_number, mm.address, mm.branch_member_number, mm.church_title
                FROM Main_Members mm
                WHERE mm.card_number = %s
            """, [card_number])

            columns = [col[0] for col in cursor.description]
            result = cursor.fetchone()

            if not result:
                return JsonResponse({'error': 'Member not found'}, status=404)

            member_data = dict(zip(columns, result))

            # Get picture data
            cursor.execute("""
                SELECT picture_data 
                FROM Member_Pictures
                WHERE Branch_Member_Number = %s
            """, [member_data.get('branch_member_number')])

            picture_row = cursor.fetchone()

            if picture_row and picture_row[0]:
                member_data['picture_url'] = f"data:image/jpeg;base64,{b64encode(picture_row[0]).decode()}"
            else:
                member_data['picture_url'] = '/static/default-profile.jpg'

            return JsonResponse(member_data)

    except Exception as e:
        print(f"Error in member_details_api: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
    
    