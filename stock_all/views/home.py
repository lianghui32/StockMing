from django.shortcuts import render, redirect


def home_all(request):
    return render(request, 'home.html')
