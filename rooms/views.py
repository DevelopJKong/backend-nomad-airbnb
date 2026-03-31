# Create your views here.
# from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

from rooms.models import Room


def see_all_rooms(request):

    rooms = Room.objects.all()
    return render(request, 'all_rooms.html', {'rooms': rooms, 'title': 'Hello! this title comes from django!'})


def see_one_room(request, room_id):
    return HttpResponse(f'one room: {room_id}')
