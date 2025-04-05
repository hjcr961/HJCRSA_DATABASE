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





@require_http_methods(["GET", "POST"])
def upload_picture(request):
    if request.method == 'POST':
        if 'picture' in request.FILES:
            picture = request.FILES['picture']
            branch_member_number = request.POST.get('branch_member_number')
            
            # First verify the member exists
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT Branch_Member_Number 
                    FROM Main_Members 
                    WHERE Branch_Member_Number = %s
                """, [branch_member_number])
                member_exists = cursor.fetchone()
                
                if not member_exists:
                    messages.error(request, 'Invalid Branch Member Number. Please enter a valid member number.')
                    return redirect('upload_picture')
            
            # Process image if member exists
            img = Image.open(picture)
            if img.mode in ('RGBA', 'P'): 
                img = img.convert('RGB')
            
            max_size = (800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=10, optimize=True)
            compressed_image = buffer.getvalue()
            
            if len(compressed_image) > 65000:
                messages.error(request, 'Image is too large. Please use a smaller image.')
                return redirect('upload_picture')
            
            # Insert the picture
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Member_Pictures (Branch_Member_Number, picture_data, upload_date) 
                    VALUES (%s, %s, %s)
                """, [branch_member_number, compressed_image, timezone.now()])
            
            messages.success(request, 'Picture uploaded successfully!')
            return redirect('home')
            
    return render(request, 'main_app/upload_picture.html')





def add_main_member(request):
    if request.method == 'POST':
        return handle_post_request(request)
    else:
        return handle_get_request(request)

def handle_post_request(request):
    form = MainMembersForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors})

    # Process dependents and calculate their count
    dependent_first_names = request.POST.getlist('dependent_first_name[]')
    dependent_last_names = request.POST.getlist('dependent_last_name[]')
    number_of_dependants = calculate_number_of_dependants(dependent_first_names)

    # Save the main member
    main_member = save_main_member(form, number_of_dependants)

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

def save_main_member(form, number_of_dependants):
    return MainMembers.objects.create(
        name=form.cleaned_data['name'],
        surname=form.cleaned_data['surname'],
        address=form.cleaned_data['address'],
        gender=form.cleaned_data['gender'],
        branch=form.cleaned_data['branch'],
        phone_number=form.cleaned_data['phone_number'],
        card_number=form.cleaned_data['card_number'],
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

@permission_required('main_app.add_treasury', raise_exception=True)
def add_treasury(request):
    if request.method == 'POST':
        form = TreasuryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treasury record added successfully!')
            return redirect('treasury_list')
    else:
        form = TreasuryForm()
    return render(request, 'main_app/add_treasury.html', {'form': form})


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
        'branch_member_number'
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
            idmain_member = request.POST.get('idmain_member')
            payment_date = request.POST.get('payment_date')
            receipt_number = request.POST.get('receipt_number')
            fund_months = request.POST.getlist('fund_date_month[]')

            # Comprehensive input validation
            if not all([fund_types, fund_years, amounts, idmain_member, 
                        payment_date, receipt_number, fund_months]):
                return JsonResponse({
                    'success': False, 
                    'error': 'All fields are required'
                }, status=400)

            # Validate list lengths match
            if not (len(fund_types) == len(fund_years) == 
                    len(amounts) == len(fund_months)):
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
            return redirect('member_list')
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



