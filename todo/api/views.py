from django.shortcuts import render,redirect ,get_object_or_404
from django.contrib.auth.models import User
from api import models
from django.contrib.auth import authenticate,login as login_auth,logout as auth_logout
from django.contrib.auth.decorators import login_required
from api.models import Todo_list
from django.http import JsonResponse
from todo.settings import api_key 
import requests

# Create your views here.


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
        user = authenticate(request,username =user,password = pwd )
        if user is not None:
            login_auth(request,user)
            return redirect('/home/')
        else:
            return render(request,'api/login.html',{'error':'Wrong Username or Password'})
        
    return render(request,'api/login.html')


def home(request):
    return render(request,'api/home.html',{'name':request.user})


@login_required(login_url='/login/')
def todo(request):
    if request.method =="POST":
        title = request.POST.get('title')
        starting_date = request.POST.get('startDate')
        expiring_date = request.POST.get('expirityDate')
        if title:
            obj = models.Todo_list(title=title, user = request.user, start_date = starting_date, expirity_date = expiring_date)
            obj.save()
            return redirect('/todo/view')
        
    return render(request,'api/todo.html',{"name":request.user})


@login_required(login_url='/login/')
def view(request):
    todo_list = models.Todo_list.objects.filter(user = request.user)
    non_expired_todos =[]
    expired_todos = []
    for todo in todo_list:
        if todo.is_expired:
            expired_todos.append(todo)
        else:
            non_expired_todos.append(todo)
    # saving completed either true or false
    if request.method == "POST":
        todo_id = request.POST.get("content-name")
        completed = "completed" in request.POST  # True if checked, False if not

        models.Todo_list.objects.filter(srno=todo_id, user=request.user).update(completed=completed)

        return redirect("/todo/view/")
        
    return render(request, 'api/view.html',{"non_expired_todos":non_expired_todos,"expired_todos":expired_todos})


@login_required(login_url='/login/')
def view_favorites(request):
    favorite_list = models.Todo_list.objects.filter(user = request.user, favorite = True)
    return render(request, 'api/favorites.html',{'favorite_list': favorite_list})


def view_completed(request):
    completed_list = models.Todo_list.objects.filter(user = request.user, completed = True)
    return render(request, 'api/completed.html',{'completed_list':completed_list})


@login_required(login_url='/login/')
def edit(request, todo_id):
    todo = get_object_or_404(Todo_list, srno=todo_id, user=request.user)
    message = ''
    print(todo.start_date)
    if request.method == "POST":
        todo.title = request.POST.get('title')
        todo.start_date = request.POST.get('start-date')
        todo.expirity_date = request.POST.get('end-date')
        todo.save()
        message = "Saved"

    return render(request, 'api/edit.html', {"todo": todo, "message": message})


def delete(request, todo_id):
    todo = get_object_or_404(Todo_list, srno=todo_id, user=request.user)
    print(todo)
    todo.delete()
    return redirect("/todo/view/")


def add_favorite(request, todo_id):
    todo = get_object_or_404(Todo_list, srno=todo_id, user=request.user)

    if request.method == "POST":
        is_favorite = 'favorite' in request.POST
        todo.favorite = is_favorite
        todo.save()
        return redirect(f'/todo/view/edit/{todo_id}/', todo_id=todo.srno)

    return render(request, 'api/view.html', {'todo': todo})


@login_required(login_url='/login/')
def logout(request):
    if request.method =="POST":
        user = request.user
        auth_logout(request)
        return render(request,'api/logout.html',{"user":user})
    
    return redirect('/login/')


@login_required(login_url='/login/')
def get_weather(request):
    weather_data = None
    if request.method =="POST":
        city = request.POST.get('city')
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        response = requests.get(url).json()

        if response.get('cod') ==200:
            weather_data ={
                'city':city.title(),
                'temp':response['main']['temp'],
                'description':response['weather'][0]['description'].title(),
                'country': response['sys']['country'],
                'humidity':response['main']['humidity'],
                'wind_speed':round(response['wind']['speed']*3.6,1),
            }
    return render(request,'api/weather.html',{'weather':weather_data})
