from django.shortcuts import render,redirect ,get_object_or_404
from django.contrib.auth.models import User
from api import models
from django.contrib.auth import authenticate,login as login_auth,logout as auth_logout
from django.contrib.auth.decorators import login_required
from api.models import Todo_list

# Create your views here.
def signUp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(username,email,password)
        my_user = User.objects.create_user(username,email,password)
        my_user.save()
        return redirect('/login/')

    
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
    if request.method =="POST":
        todo.title = request.POST.get('title')
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