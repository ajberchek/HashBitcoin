from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    print("Try\n")
    return render(request=request, template_name='LAHacksProject.html')

# Create your views here.
