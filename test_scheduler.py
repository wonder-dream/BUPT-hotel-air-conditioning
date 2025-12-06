import os
import sys
import time
import django

# 设置 Django 环境
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_ac.settings")
django.setup()

from ac_system.scheduler import scheduler
from ac_system.models import Room


def test_scheduler():
    print("Starting scheduler test...")

    # 确保有房间数据
    if not Room.objects.exists():
        print("Creating test rooms...")
        for i in range(1, 6):
            Room.objects.create(
                room_id=f"30{i}", room_type="standard", price_per_day=400
            )

    # 启动调度器
    scheduler.start()
    print("Scheduler started.")

    # 模拟开机请求
    print("Submitting power_on request for 301...")
    scheduler.submit_request(
        "301",
        {
            "action": "power_on",
            "target_temp": 22,
            "fan_speed": "high",
            "mode": "cooling",
        },
    )

    # 观察几秒
    for i in range(5):
        state = scheduler.get_room_state("301")
        print(
            f"Time {i}: Temp={state['current_temp']}, Status={state['status']}, Cost={state['cost']}"
        )
        time.sleep(1)

    # 模拟调温
    print("Changing temp for 301...")
    scheduler.submit_request(
        "301", {"action": "change_temp", "target_temp": 20, "mode": "cooling"}
    )

    for i in range(3):
        state = scheduler.get_room_state("301")
        print(
            f"Time {i+5}: Temp={state['current_temp']}, Target={state['target_temp']}"
        )
        time.sleep(1)

    # 停止调度器
    scheduler.stop()
    print("Test finished.")


if __name__ == "__main__":
    test_scheduler()
