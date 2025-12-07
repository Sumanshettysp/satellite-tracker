# test_simple.py
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Simple test works!")
