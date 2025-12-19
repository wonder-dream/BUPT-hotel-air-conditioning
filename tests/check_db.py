import os
import sys
import django

# 设置 Django 环境 (从 tests 目录向上一级到项目根目录，再进入 backend)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_ac.settings")
django.setup()

from ac_system.models import Room

rooms = Room.objects.all()
print(f"Total rooms: {rooms.count()}")
for room in rooms:
    print(f"Room {room.room_id}: {room.status}")
