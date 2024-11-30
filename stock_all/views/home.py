from django.shortcuts import render, redirect
from django.urls import reverse


def home_all(request):
    return render(request, 'home.html')
