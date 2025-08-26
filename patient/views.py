from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum, Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels
from . import models as patient_models
from blood import models as blood_models
from django.contrib.auth import logout


def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    mydict = {'userForm': userForm, 'patientForm': patientForm}
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.bloodgroup = patientForm.cleaned_data['bloodgroup']
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request, 'patient/patientsignup.html', context=mydict)


def make_request_view(request):
    request_form = bforms.RequestForm()
    if request.method == 'POST':
        request_form = bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request = request_form.save(commit=False)
            blood_request.bloodgroup = request_form.cleaned_data['bloodgroup']
            patient = models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient = patient
            blood_request.save()
            return HttpResponseRedirect('my-request')  
    return render(request, 'patient/makerequest.html', {'request_form': request_form})



@login_required
def my_request_view(request):
    patient = patient_models.Patient.objects.get(user_id=request.user.id)

    # Get filter parameter
    status_filter = request.GET.get('status', 'all')
    
    # Get all requests for this patient
    all_requests = blood_models.BloodRequest.objects.filter(request_by_patient=patient).order_by('-date')
    
    # Apply filter
    if status_filter == 'pending':
        blood_request = all_requests.filter(status='Pending')
    elif status_filter == 'approved':
        blood_request = all_requests.filter(status='Approved')
    elif status_filter == 'rejected':
        blood_request = all_requests.filter(status='Rejected')
    else:
        blood_request = all_requests
    
    # Get counts for summary
    total_requests = all_requests.count()
    pending_count = all_requests.filter(status='Pending').count()
    approved_count = all_requests.filter(status='Approved').count()
    rejected_count = all_requests.filter(status='Rejected').count()
    
    context = {
        'blood_request': blood_request,
        'current_filter': status_filter,
        'total_requests': total_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'patient/my_request.html', context)


def patient_logout_view(request):
    logout(request)
    return redirect('patientlogin')
