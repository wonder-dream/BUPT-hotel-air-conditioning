"""
初始化数据脚本
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_ac.settings")
django.setup()

from ac_system.models import Room
from config import ROOM_PRICE


def init_rooms():
    """初始化房间数据"""
    rooms_data = [
        {
            "room_id": "301",
            "room_type": "standard",
            "price_per_day": ROOM_PRICE["standard"],
        },
        {
            "room_id": "302",
            "room_type": "standard",
            "price_per_day": ROOM_PRICE["standard"],
        },
        {
            "room_id": "303",
            "room_type": "deluxe",
            "price_per_day": ROOM_PRICE["deluxe"],
        },
        {
            "room_id": "304",
            "room_type": "deluxe",
            "price_per_day": ROOM_PRICE["deluxe"],
        },
        {"room_id": "305", "room_type": "suite", "price_per_day": ROOM_PRICE["suite"]},
    ]

    for room_data in rooms_data:
        room, created = Room.objects.get_or_create(
            room_id=room_data["room_id"],
            defaults={
                "room_type": room_data["room_type"],
                "price_per_day": room_data["price_per_day"],
                "status": "available",
            },
        )
        if created:
            print(f"Created room: {room.room_id}")
        else:
            print(f"Room exists: {room.room_id}")


if __name__ == "__main__":
    print("Initializing data...")
    init_rooms()
    print("Data initialization completed!")
