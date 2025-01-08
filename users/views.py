from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import Group

def home(request):
    return render(request, "user.html")

def logout_view(request):
    logout(request)
    return redirect("/")

