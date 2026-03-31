# Create your views here.
# from django.shortcuts import render
from django.http import HttpResponse


def see_all_rooms(request):
    return HttpResponse('all rooms')


def see_one_room(request, room_id):
    return HttpResponse(f'one room: {room_id}')
