import csv
import requests
import joblib
import pandas as pd
import numpy as np
import string
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression#importing the sklearn.linear_model.LogisticRegression module which will be used in this porjectfrom bs4 import BeautifulSoup as bs
from bs4 import BeautifulSoup as bs
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from . import models
from . import utils


def index(request):
    if request.user.username:
        user_details = models.user.objects.get(username=request.user.username)
        context = {'user_details': user_details}
        return render(request, 'index.html',context)
    else:
        return render(request, "index.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        role = request.POST.get('role')
        name = request.POST.get('name')
        
        if pass1 == pass2:
            existemail = User.objects.filter(email=email).exists()
            existusername = User.objects.filter(username=username).exists()
            if existemail or existusername:
                messages.info(request,'Email or username Already Used')
                return redirect('signup')
            else:
                user = User.objects.create_user(username,email,pass1)
                user.first_name=name
                user.save()
                user1 = models.user(username=username,email=email,name=name,role=role)
                user1.save()
                return redirect('login')
        else :
            messages.info(request,"User pass and confirm pass not match")
            return redirect('signup')
    return render(request, 'signup.html')

def Login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request,"Username or Password is incorrect")
            return redirect('login')
    else:        
        return render(request, 'login.html')

def Logout(request):
    auth.logout(request)
    return redirect('index')

@login_required(login_url='login')
def extract_review(request):
    if request.method == 'POST':
        url = request.POST['url']
        n = int(request.POST['n'])
        reviews = []

        page = requests.get(url)
        soup = bs(page.content,'html.parser')

        # product Name
        product_name=soup.find('div',class_='_2s4DIt').get_text().strip()

        # product image
        product_img=soup.find('img' ,class_="_396cs4")
        product_img=product_img.get('src')

        # product Price
        product_price=soup.find('div',class_='_30jeq3').get_text().strip()

        review1 = models.review(username=request.user.username,title=product_name,product_url=url)
        review1.save()
        # review
        for i in range(1, n + 1):
            page_url = url + f'&page={i}'
            page = requests.get(page_url)
            soup = bs(page.content, 'html.parser')
            review_containers = soup.find_all('div', class_='_27M-vq')
            for container in review_containers:
                title = container.find('p', class_='_2-N8zT').get_text().strip()
                content = container.find('div', class_='t-ZTKy').get_text().strip()
                content = content.replace('READ MORE', '.').strip()
                user_name = container.find('p',class_='_2sc7ZR _2V5EHH').get_text().strip()
                reviews.append({'title': title, 'content': content, 'user_name': user_name})

        # Save reviews into CSV file
        with open('CSV/reviews.csv', mode='w', newline='',encoding='utf-8') as csv_file:
            fieldnames = ['title', 'content', 'user_name']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for review in reviews:
                writer.writerow(review)
        
        x = pd.read_csv('../fake_review/CSV/reviews.csv')
        newContent = x["content"]
        newContent = newContent.apply(utils.convertmyTxt)
        model = load_model()

        Status = model.predict(newContent)
        x['Label'] = Status.tolist()
        x.to_csv('../fake_review/CSV/new_reviews_with_labels.csv', index=False)
       
        i=0
        for review in reviews:
            review['Status'] = Status[i]
            i+=1
        real_count = np.count_nonzero(Status == 'REAL')
        fake_count = np.count_nonzero(Status == 'FAKE')

        total_count = len(Status)
        Real_percentage = ((real_count/total_count)*100)
        Fake_percentage = ((fake_count/total_count)*100)
        if request.user.username:
            user_details = models.user.objects.get(username=request.user.username)
        context = {'reviews': reviews, 'product_name': product_name, 'product_img': product_img, 'product_price': product_price, 'url': url,'R_P':Real_percentage, 'F_P':Fake_percentage, 'user_details': user_details}
        return render(request, 'extract_review.html', context)
    else:
        return render(request, 'index.html')

def load_model():
    # Create the pipeline
    pipeline = Pipeline([
        ('bow', CountVectorizer(analyzer=utils.convertmyTxt)),
        ('tfidf', TfidfTransformer()),
        ('classifier', LogisticRegression())
    ])
    # Load the saved model
    model = joblib.load('../fake_review/CSV/classifier.pkl')
    return model

def check(request):
    if request.method=='POST':
        text = request.POST['text']
        model = load_model()
        Status = model.predict([text])
        context = {'Status':Status}
        return render(request, 'reviewchecker.html', context)
    else:
        return render(request, 'reviewchecker.html')