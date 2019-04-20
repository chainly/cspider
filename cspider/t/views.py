from django.shortcuts import render

# Create your views here.
def xterm(request):
    return render(request, 'xterm.html')
