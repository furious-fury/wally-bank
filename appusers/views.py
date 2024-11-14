from django.shortcuts import render, redirect , get_object_or_404
app_name="appusers"
from django.http import HttpResponse
from .models import *
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import *
from .forms import KYCForm
from decimal import Decimal  # Import Decimal module
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.utils import timezone


def index(request):
    return render(request, 'index.html')
    
def about(request):
    return render(request, 'about.html')

def card(request):
    return render(request, 'card.html')
    
def loan(request):
    return render(request, 'loan.html')
    

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, you can redirect to a success page
            return redirect('/dashboard')  # Replace 'success_url_name' with the name of your success URL
            messages.success(request, 'Your message delivered successfully')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})    


@login_required
def dashboard(request):
    user_profile, created  = userprofile.objects.get_or_create(user=request.user)
    # Pass user_profile as a list even if it's a single object
    user_profile_list = [user_profile]
   
    # Retrieve the 5 most recent transaction history records
    transaction_history = TransactionHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    data = {'user_profile':user_profile_list,'transaction_history': transaction_history }
    return render(request, 'dashboard.html', data)
    
#def deposit(request):
    #if request.method == 'POST':
       # amount = request.POST.get('amount')
       # account = request.POST.get('account')
       # image = request.FILES.get('image')
        # You may need to validate the form data here

        # Save deposit details to the database
        #transaction = TransactionHistory.objects.create(
        #    user=request.user,
        #    amount=amount,
        #    status='Pending'
        #)
        #transaction.save()

        # Handle image upload here if needed

    #    messages.success(request, 'Deposit request submitted successfully!')
    #    return redirect('/dashboard')  # Redirect to the same page after submission
    #data = {}
    #return render(request, 'deposit.html', data)


@login_required
def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            # Save deposit data to the database
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.save()
            
            # Display success message
            messages.success(request, 'Your deposit is under review...')
            
            # Create a transaction history record
            TransactionHistory.objects.create(
                user=request.user,
                amount=deposit.amount,
                transaction_type='deposit',
                description='Deposit made',
                status='pending',
            )
            
            return redirect('/dashboard')  # Redirect to dashboard after successful deposit
        else:
            # Display an error message if the available balance is insufficient
            error_message = "Insufficient balance. Please check your available balance."
    else:
        form = DepositForm()
        # Display an error message if the available balance is insufficient
        error_message = "Insufficient balance. Please check your available balance."
    
    return render(request, 'deposit.html', {'form': form})



@login_required
def local_transfer(request):
    if request.method == 'POST':
        form = LocalTransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_profile = userprofile.objects.get(user=request.user)
            if user_profile.avaliablebalance >= amount:
                # Convert Decimal to string before saving to session
                form.cleaned_data['amount'] = str(amount)
                # Save the form data in the session for later use
                request.session['local_transfer_form_data'] = form.cleaned_data

                # Redirect to the PIN verification page
                return redirect('/pin')  # URL for PIN verification
            else:
                # Display an error message if the available balance is insufficient
                error_message = "Insufficient balance. Please check your available balance."
                return render(request, 'local_transfer.html', {'form': form, 'error_message': error_message})
    else:
        form = LocalTransferForm()

    return render(request, 'local_transfer.html', {'form': form})


@login_required
def withdraw(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_profile = userprofile.objects.get(user=request.user)
            if user_profile.avaliablebalance >= amount:
                # Convert Decimal to string before saving to session
                form.cleaned_data['amount'] = str(amount)
                # Save the form data in the session for later use
                request.session['withdraw_form_data'] = form.cleaned_data

                # Redirect to the PIN verification page
                return redirect('/pin')  # URL for PIN verification
            else:
                # Display an error message if the available balance is insufficient
                error_message = "Insufficient balance. Please check your available balance."
                return render(request, 'withdraw.html', {'form': form, 'error_message': error_message})
    else:
        form = WithdrawForm()

    return render(request, 'withdraw.html', {'form': form})

@login_required
def pin(request):
    if request.method == 'POST':
        form = PinVerificationForm(request.POST)
        if form.is_valid():
            pin = form.cleaned_data['pin']
            user_pin = PIN.objects.filter(pin=pin).exists()
            if user_pin:
                # PIN is valid, process the form data from the session
                if 'local_transfer_form_data' in request.session:
                    form_data = request.session.pop('local_transfer_form_data')
                    amount = Decimal(form_data['amount'])  # Convert back to Decimal
                    # Create LocalTransfer object and transaction history
                    # Adjust this part based on your model structure
                    transfer = LocalWithdrawal.objects.create(user=request.user, **form_data)
                    TransactionHistory.objects.create(
                        user=request.user,
                        amount=transfer.amount,
                        accountnumber=transfer.account_number,
                        transaction_type='transfer',
                        description='Local transfer made',
                        status='pending',
                    )
                    # Deduct the amount from available balance
                    user_profile = userprofile.objects.get(user=request.user)
                    user_profile.avaliablebalance -= amount
                    user_profile.save()
                    messages.success(request, 'Local transfer completed successfully.')
                elif 'withdraw_form_data' in request.session:
                    form_data = request.session.pop('withdraw_form_data')
                    amount = Decimal(form_data['amount'])  # Convert back to Decimal
                    # Create Withdraw object and transaction history
                    # Adjust this part based on your model structure
                    withdraw = Withdraw.objects.create(user=request.user, **form_data)
                    TransactionHistory.objects.create(
                        user=request.user,
                        amount=withdraw.amount,
                        accountname=withdraw.accountname,
                        accountnumber=withdraw.accountnumber,
                        transaction_type='withdrawal',
                        description='Withdrawal made',
                        status='pending',
                    )
                    # Deduct the amount from available balance
                    user_profile = userprofile.objects.get(user=request.user)
                    user_profile.avaliablebalance -= amount
                    user_profile.save()
                    messages.success(request, 'Withdrawal completed successfully.')
                return redirect('/dashboard')
            else:
                # PIN is invalid, display error message
                messages.error(request, 'Invalid PIN. Please try again.')
    else:
        form = PinVerificationForm()

    return render(request, 'pin.html', {'form': form})







   
 
@login_required
def cards(request):
    return render(request, 'cards.html', )
    
    
    
@login_required
def history(request):
    # Retrieve transaction history records associated with the current user
    transaction_history = TransactionHistory.objects.filter(user=request.user)

    return render(request, 'history.html', {'transaction_history': transaction_history})

    
@login_required    
def kyc(request):
    if request.method == 'POST':
        form = KYCForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your Kyc is under review...')
            return redirect('/dashboard')  # Redirect to a success page
    else:
        form = KYCForm()
    return render(request, 'kyc.html', {'form': form}) 


@login_required
def loans(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your loan request is under review...')
            return redirect('/dashboard')  # Redirect to a success page
    else:
        form = LoanRequestForm()
    return render(request, 'loans.html', {'form': form})



@login_required    
def success(request):

    return render(request, 'success.html', )



def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'You have signed up successfully.')
            login(request, user)
            return redirect('/login')
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {'form': form})


def user_login(request):

    if request.method == 'GET':
        form = LoginForm()
        return render(request,'registration/login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome!')
                return redirect('/dashboard')
            else:
                # If authentication fails, show error message
                messages.error(request, 'Invalid username or password')
                return render(request, 'registration/login.html', {'form': form})
        else:
            # form is not valid or user is not authenticated
            messages.error(request,f'Invalid username or password')
            return render(request,'registration/login.html',{'form': form})
        
def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('login')  # Redirect to the login page or home page