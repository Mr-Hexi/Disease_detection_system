import os
import uuid
import warnings
from home.brain_tumor import * 
from home.predictions import *
from .models import MedReport
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login , logout    
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect




warnings.filterwarnings("ignore", message="A NumPy version >=1.16.5 and <1.23.0 is required for this version of SciPy")



MODEL_WEIGHTS = "C:\Huzaifa\Deep-Learning-Projects\Multiple_Disease_Detection\MRI_Detection\models\clf-resnet-weights.hdf5"
SEG_MODEL_WEIGHTS = "C:\Huzaifa\Deep-Learning-Projects\Multiple_Disease_Detection\MRI_Detection\models\ResUNet-segModel-weights.hdf5"

bt_model = load_resnet(MODEL_WEIGHTS)
bt_seg_model = load_unet(SEG_MODEL_WEIGHTS)

pna_model = tf.keras.models.load_model("models\VGG16_modelh5.h5")
ret_model = tf.keras.models.load_model('models\\retina_95_acc_VGG.h5')








def handle_login(request):
    if request.method == 'POST':
        loginusername = request.POST['username']
        loginpassword = request.POST['password']
        # user = authenticate(username=loginusername, password=loginpassword)
        if user is not None:   
            # login(request, user)  
            messages.success(request, "Successfully Logged In")
            return redirect('home')
        else:
            error_message = "Invalid credentials! Please try again"
            return render(request, 'login.html', {'error_message': error_message})
    
    return render(request, 'login.html')

@login_required
def handleLogout(request):
    # if request.user.is_superuser or request.user.is_staff:
    #     # don't allow superusers/admins to be logged out using this view
    #     return redirect('home')
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('home') 
# def handelLogout(request):
#     logout(request)
#     messages.success(request, "Successfully logged out")
#     return redirect('home')


@login_required
def profile(request):
    user = request.user
    first_name = request.user.first_name
    reports = MedReport.objects.filter(user=user).order_by('-patient_id').all()

    context = {
        'first_name': first_name,
        'active_page': 'profile',
        'reports': reports,
    }
    return render(request, 'profile.html',context)


@login_required
def home(request):
    return render(request, 'index.html',{'active_page': 'home'})


@login_required
def braintumor(request):
    return render(request, 'brain_tumor.html',{'active_page': 'services'})


@login_required
def pneumonia(request):
    return render(request, 'pneumonia.html',{'active_page': 'services'})

@login_required
def retinal(request):
    return render(request, 'retinal.html',{'active_page': 'services'})

@login_required
def contact(request):
    if request.method == 'POST':
        full_name = request.POST['FullName']
        email = request.POST['Email']
        message = request.POST['Message']
        return HttpResponse('Thank you for your message!')
    return render(request, 'contact.html')

@login_required    
def btpred(request):
    if request.method == 'POST' and request.FILES['file']:
        fileobj = request.FILES['file']
        fullname = request.POST['fullname']
        email = request.POST['email']
        phone = request.POST['phone']
        gender = request.POST['gender']
        age = request.POST['age']
        
        
        
        fs = FileSystemStorage()
        filename = fs.save(fileobj.name, fileobj)
        file_url = fs.url(filename)
        f_path = os.path.join("media/",filename)
        

        preds,bt_pred= bt_predict(f_path,bt_model,bt_seg_model)
        print(bt_pred)
        if preds == 0:
            result = 'No TUMOR Detected'
            fname = "media/no_bt.jpg"
        else:
            result = 'TUMOR Detected'
            fname = "media/bt_seg.jpg"
            
        med_report = MedReport(
            user= request.user,
            date=timezone.now().date(),
            fullname=fullname,
            email=email,
            phone=phone,
            gender=gender,
            age=age,
            img=filename,
            test_type="Brain Tumor Detection",
            results=result,
        )
        med_report.save()

        return render(request, 'btpred.html', {
                'patient_id':med_report.patient_id,
                'data': result,
                'filename': fname,
                'fn': fullname,
                'age': age,
                'gender': gender
            })

    return HttpResponse('Invalid request') 

@login_required
def pnapred(request):
    if request.method == 'POST' and request.FILES['file']:
        fileobj = request.FILES['file']
        fullname = request.POST['fullname']
        email = request.POST['email']
        phone = request.POST['phone']
        gender = request.POST['gender']
        age = request.POST['age']

        fs = FileSystemStorage()
        filename = fs.save(fileobj.name, fileobj)
        file_url = fs.url(filename)
        f_path = os.path.join("media/",filename)
        
        
        
        results = pneumonia_predict(f_path,pna_model)

        med_report = MedReport(
                user= request.user,
                date=timezone.now().date(),
                fullname=fullname,
                email=email,
                phone=phone,
                gender=gender,
                age=age,
                img=filename,
                test_type="Pneumonia Detection",
                results=results,
            )
        med_report.save()
        return render(request, 'pnapred.html', {
                'patient_id':med_report.patient_id,
                'data': results,
                'filename': f_path,
                'fn': fullname,
                'age': age,
                'gender': gender
            })

    return HttpResponse('Invalid request') 


@login_required
def retpred(request):
    if request.method == 'POST' and request.FILES['file']:
        fileobj = request.FILES['file']
        fullname = request.POST['fullname']
        email = request.POST['email']
        phone = request.POST['phone']
        gender = request.POST['gender']
        age = request.POST['age']
        
        fs = FileSystemStorage()
        filename = fs.save(fileobj.name, fileobj)
        file_url = fs.url(filename)
        f_path = os.path.join("media/",filename)
        results = ret_predict(f_path,ret_model)
        
        med_report = MedReport(
                user= request.user,
                date=timezone.now().date(),
                fullname=fullname,
                email=email,
                phone=phone,
                gender=gender,
                age=age,
                img=filename,
                test_type="Retinal Disorder Detection",
                results=results,
            )
        med_report.save()
        return render(request, 'retpred.html', {
                    'patient_id':med_report.patient_id,
                    'data': results,
                    'filename': f_path,
                    'fn': fullname,
                    'age': age,
                    'gender': gender
                })
        

    return HttpResponse('Invalid request')

        