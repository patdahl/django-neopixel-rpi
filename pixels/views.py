from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "pixels/index.html")

def room(request, room_name):
    return render(request, "pixels/room.html", {"room_name": room_name})