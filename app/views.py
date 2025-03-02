from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'index.html')  # Pointing to templates/home.html
