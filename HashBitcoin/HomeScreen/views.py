from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("You successfully made it to our home page!")

# Create your views here.
