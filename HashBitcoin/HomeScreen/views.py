from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    print("Try")
    return render(request=request, template_name='Test.html')

# Create your views here.
