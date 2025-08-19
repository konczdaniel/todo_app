from django.shortcuts import render,redirect ,get_object_or_404
from django.contrib.auth.models import User
from api import models
from django.contrib.auth import authenticate,login as login_auth,logout as auth_logout
from django.contrib.auth.decorators import login_required
from api.models import Todo_list
from django.http import JsonResponse
from todo.settings import api_key as key
import requests

# Create your views here.
def get_weather(request):
    city = request.GET.get('city')
    if not city:
        return JsonResponse({'error': 'City parameter is required'}, status=400)

    api_key = key
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse({'error': 'City not found'}, status=response.status_code)

    data = response.json()

    return JsonResponse({
        'city': data['name'],
        'temperature': data['main']['temp'],
        'description': data['weather'][0]['description'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
    })


def user_verifier(username, all_usernames):
    for user in all_usernames:
        if user == username:
            return False  
    return True  


def signUp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        all_usernames = User.objects.values_list('username', flat=True)
        user_bool = user_verifier(username,all_usernames)
        if user_bool:
            my_user = User.objects.create_user(username,email,password)
            my_user.save()
            return redirect('/login/')
        else:
            return render(request,'api/signup.html',{'error_message':'username already exists, Log in'})

    return render(request,"api/signup.html")


def login(request):
    if request.method =="POST":
        user = request.POST.get('username')
        pwd = request.POST.get('password')
        print(user,pwd)
        user = authenticate(request,username =user,password = pwd )
        if user is not None:
            login_auth(request,user)
            return redirect('/todo/')
        else:
            return redirect('/login/')
        
    return render(request,'api/login.html')


@login_required(login_url='/login/')
def todo(request):
    if request.method =="POST":
        title = request.POST.get('title')
        if title:
            obj = models.Todo_list(title=title, user = request.user)
            obj.save()
            return redirect('/todo/view')
        
    return render(request,'api/todo.html',{"name":request.user})


def view(request):
    todo_list = models.Todo_list.objects.filter(user = request.user)
    
    return render(request, 'api/view.html',{"todo_list":todo_list})


def edit(request,todo_id):
    todo = get_object_or_404(Todo_list, srno=todo_id, user=request.user)
    if request.method =="PUT":
        todo.title = request.PUT.get('title')
        todo.save()
        return render(request,'api/edit.html',{"message":"Saved"})
        
    return render(request,'api/edit.html',{"todo":todo})

def delete(request, todo_id):
    todo = get_object_or_404(Todo_list, srno=todo_id, user=request.user)
    print(todo)
    todo.delete()
    return redirect("/todo/view/")

def logout(request):
    if request.method =="POST":
        user = request.user
        auth_logout(request)
        return render(request,'api/logout.html',{"user":user})
    
    return redirect('/login/')