import os
import sys
import django

sys.path.append(os.path.join(os.getcwd(), "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_ac.settings")
django.setup()

from ac_system.models import Room

rooms = Room.objects.all()
print(f"Total rooms: {rooms.count()}")
for room in rooms:
    print(f"Room {room.room_id}: {room.status}")
