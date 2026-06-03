from django.shortcuts import render, redirect

# store active rooms in memory
active_rooms = {}

def index(request):
    return render(request, 'app/index.html')


def room(request):
    username = request.GET.get('username')
    room_name = request.GET.get('room')

    if not username or not room_name:
        return redirect('/')

    if room_name not in active_rooms:
        active_rooms[room_name] = []

    # allow only 2 users
    if len(active_rooms[room_name]) >= 2:
        return render(request, 'app/index.html', {
            'error': 'Room is already full'
        })

    active_rooms[room_name].append(username)

    return render(request, 'app/room.html', {
        'username': username,
        'room_name': room_name,
    })