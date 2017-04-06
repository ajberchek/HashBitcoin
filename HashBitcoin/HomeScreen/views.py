from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    cookieVal = request.COOKIES.get("TotalHashes",None)
    cont = {"TotalHashes":cookieVal}
    return render(context=cont,request=request, template_name='LAHacksProject.html')

