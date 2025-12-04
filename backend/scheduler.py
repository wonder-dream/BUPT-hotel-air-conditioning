"""
空调调度服务 - 核心调度逻辑
实现优先级调度 + 时间片调度

架构设计：
- ACScheduler（调度对象）：只负责调度决策，管理队列
- ACServiceManager（服务对象）：负责温控、计费、详单记录等实际操作
"""

import threading
import time
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from typing import Dict, List, Optional, Tuple
import logging

import sys
import os

# 引入 Django 模型
from .models import ACDetailRecord, AccommodationOrder, Room

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    MAX_SERVICE_NUM,
    WAIT_TIME_SLICE,
    DEFAULT_TEMP,
    INITIAL_ROOM_TEMP,
    FAN_SPEED_POWER,
    TEMP_CHANGE_RATE,
    TEMP_RESTORE_RATE,
    PRICE_PER_DEGREE,
    FAN_SPEED_PRIORITY,
    COOLING_MIN_TEMP,
    COOLING_MAX_TEMP,
    HEATING_MIN_TEMP,
    HEATING_MAX_TEMP,
    TEMP_THRESHOLD,
)

logger = logging.getLogger(__name__)


# ============================================================
# 数据类：ServiceObject 和 WaitingObject
# ============================================================


class ServiceObject:
    """服务对象数据 - 正在接受服务的房间"""

    def __init__(self, room_id: str, target_temp: float, fan_speed: str, mode: str):
        self.room_id = room_id
        self.target_temp = target_temp
        self.fan_speed = fan_speed
        self.mode = mode  # 'cooling' or 'heating'
        self.service_start_time = datetime.now()
        self.service_duration = 0  # 服务时长（秒）
        self.current_temp = INITIAL_ROOM_TEMP
        self.energy_consumed = 0.0  # 耗电量
        self.cost = Decimal("0.00")  # 费用
        self.record_id = None  # 关联的详单记录ID

    def get_priority(self) -> int:
        """获取优先级"""
        return FAN_SPEED_PRIORITY.get(self.fan_speed, 0)

    def update_service_duration(self):
        """更新服务时长"""
        self.service_duration = (
            datetime.now() - self.service_start_time
        ).total_seconds()


class WaitingObject:
    """等待对象数据 - 在等待队列中的房间（停止送风和计费）"""

    def __init__(self, room_id: str, target_temp: float, fan_speed: str, mode: str):
        self.room_id = room_id
        self.target_temp = target_temp
        self.fan_speed = fan_speed
        self.mode = mode
        self.wait_start_time = datetime.now()
        self.wait_duration = WAIT_TIME_SLICE  # 分配的等待时长
        self.current_temp = INITIAL_ROOM_TEMP
        self.waited_full_slice = False  # 是否已等待满一个时间片
        self.energy_consumed = 0.0  # 等待期间不计费
        self.cost = Decimal("0.00")  # 等待期间不计费
        self.record_id = None  # 关联的详单记录ID

    def get_priority(self) -> int:
        """获取优先级"""
        return FAN_SPEED_PRIORITY.get(self.fan_speed, 0)

    def get_remaining_wait_time(self) -> float:
        """获取剩余等待时间"""
        elapsed = (datetime.now() - self.wait_start_time).total_seconds()
        return max(0, self.wait_duration - elapsed)

    def is_wait_expired(self) -> bool:
        """等待时间是否已到"""
        return self.get_remaining_wait_time() <= 0


# ============================================================
# ACServiceManager（服务对象）- 负责温控、计费、详单记录
# ============================================================


class ACServiceManager:
    """
    服务对象 - 负责直接进行调温、计费等操作

    职责：
    1. 更新房间温度（制冷/制热）
    2. 计算能耗和费用
    3. 管理详单记录（创建、更新、结束）
    4. 管理房间状态
    """

    def __init__(self):
        self.room_states: Dict[str, dict] = {}  # 所有房间状态

    def init_room(self, room_id: str):
        """初始化房间空调状态（入住时调用）"""
        self.room_states[room_id] = {
            "current_temp": INITIAL_ROOM_TEMP,
            "target_temp": DEFAULT_TEMP,
            "is_on": False,
            "status": "off",
            "fan_speed": "medium",
            "mode": "cooling",
            "energy_consumed": 0,
            "cost": 0,
        }
        logger.info(f"[ServiceManager] Room {room_id} AC initialized")

    def clear_room(self, room_id: str) -> dict:
        """清理房间状态（退房时调用）"""
        state = self.get_room_state(room_id)
        if room_id in self.room_states:
            del self.room_states[room_id]
        logger.info(
            f"[ServiceManager] Room {room_id} cleared, AC cost: {state.get('cost', 0)}"
        )
        return state

    def update_room_status(self, room_id: str, status: str, **kwargs):
        """更新房间状态"""
        if room_id not in self.room_states:
            self.room_states[room_id] = {
                "current_temp": INITIAL_ROOM_TEMP,
                "is_on": False,
                "status": "off",
            }

        self.room_states[room_id]["status"] = status
        self.room_states[room_id]["is_on"] = status in ("on", "waiting", "standby")

        for key, value in kwargs.items():
            self.room_states[room_id][key] = value

    def get_room_state(self, room_id: str) -> dict:
        """获取房间基本状态"""
        if room_id in self.room_states:
            state = self.room_states[room_id]
            return {
                "room_id": room_id,
                "is_on": state.get("is_on", False),
                "status": state.get("status", "off"),
                "current_temp": round(state.get("current_temp", INITIAL_ROOM_TEMP), 1),
                "target_temp": state.get("target_temp", DEFAULT_TEMP),
                "fan_speed": state.get("fan_speed", "medium"),
                "mode": state.get("mode", "cooling"),
                "energy_consumed": state.get("energy_consumed", 0),
                "cost": state.get("cost", 0),
            }
        else:
            return {
                "room_id": room_id,
                "is_on": False,
                "status": "off",
                "current_temp": INITIAL_ROOM_TEMP,
                "target_temp": DEFAULT_TEMP,
                "fan_speed": "medium",
                "mode": "cooling",
                "energy_consumed": 0,
                "cost": 0,
            }

    def update_service_temperature(self, service_obj: ServiceObject):
        """
        更新服务中房间的温度和费用

        这是服务对象的核心功能：执行实际的温控操作
        """
        service_obj.update_service_duration()

        rate = TEMP_CHANGE_RATE.get(service_obj.fan_speed, 0.5) / 60  # 转换为每秒
        power = FAN_SPEED_POWER.get(service_obj.fan_speed, 0.5) / 60  # 转换为每秒

        if service_obj.mode == "cooling":
            if service_obj.current_temp > service_obj.target_temp:
                service_obj.current_temp -= rate
                service_obj.energy_consumed += power
                service_obj.cost += Decimal(str(power * PRICE_PER_DEGREE))
        else:  # heating
            if service_obj.current_temp < service_obj.target_temp:
                service_obj.current_temp += rate
                service_obj.energy_consumed += power
                service_obj.cost += Decimal(str(power * PRICE_PER_DEGREE))

        # 同步更新房间状态
        room_id = service_obj.room_id
        if room_id in self.room_states:
            self.room_states[room_id]["current_temp"] = service_obj.current_temp
            self.room_states[room_id]["energy_consumed"] = service_obj.energy_consumed
            self.room_states[room_id]["cost"] = float(service_obj.cost)

    def update_waiting_state(self, wait_obj: WaitingObject):
        """更新等待中房间的状态（不改变温度，不计费）"""
        room_id = wait_obj.room_id
        if room_id in self.room_states:
            self.room_states[room_id]["current_temp"] = wait_obj.current_temp
            self.room_states[room_id]["energy_consumed"] = wait_obj.energy_consumed
            self.room_states[room_id]["cost"] = float(wait_obj.cost)

    def update_off_room_temperature(self, room_id: str):
        """更新关机房间的温度（回温）"""
        if room_id not in self.room_states:
            return

        state = self.room_states[room_id]
        if state.get("status") != "off":
            return

        rate = TEMP_RESTORE_RATE / 60
        current = state.get("current_temp", INITIAL_ROOM_TEMP)

        if current < INITIAL_ROOM_TEMP:
            state["current_temp"] = min(current + rate, INITIAL_ROOM_TEMP)
        elif current > INITIAL_ROOM_TEMP:
            state["current_temp"] = max(current - rate, INITIAL_ROOM_TEMP)

    def check_target_reached(self, service_obj: ServiceObject) -> bool:
        """检查是否达到目标温度"""
        if service_obj.mode == "cooling":
            return service_obj.current_temp <= service_obj.target_temp
        else:
            return service_obj.current_temp >= service_obj.target_temp

    def check_need_restart(self, room_id: str) -> bool:
        """检查待机房间是否需要重新启动"""
        if room_id not in self.room_states:
            return False

        state = self.room_states[room_id]
        if state.get("status") != "standby":
            return False

        current_temp = state.get("current_temp", DEFAULT_TEMP)
        target_temp = state.get("target_temp", DEFAULT_TEMP)
        mode = state.get("mode", "cooling")

        if mode == "cooling":
            return current_temp > target_temp + TEMP_THRESHOLD
        else:
            return current_temp < target_temp - TEMP_THRESHOLD

    # ========== 详单记录管理 ==========

    def create_detail_record(self, service_obj: ServiceObject):
        """创建详单记录"""
        try:
            order = AccommodationOrder.objects.filter(
                room_id=service_obj.room_id, status="active"
            ).first()

            record = ACDetailRecord.objects.create(
                room_id=service_obj.room_id,
                order=order,
                start_time=timezone.now(),
                start_temp=service_obj.current_temp,
                target_temp=service_obj.target_temp,
                fan_speed=service_obj.fan_speed,
                mode=service_obj.mode,
                energy_consumed=0,
                cost=0,
            )
            service_obj.record_id = record.record_id
            logger.info(
                f"[ServiceManager] Created detail record {record.record_id} for room {service_obj.room_id}"
            )
        except Exception as e:
            logger.error(f"[ServiceManager] Failed to create detail record: {e}")

    def end_detail_record(self, service_obj: ServiceObject):
        """结束详单记录"""
        if not service_obj.record_id:
            return

        try:
            record = ACDetailRecord.objects.get(record_id=service_obj.record_id)
            record.end_time = timezone.now()
            record.end_temp = service_obj.current_temp
            record.energy_consumed = service_obj.energy_consumed
            record.cost = service_obj.cost
            record.save()
            logger.info(
                f"[ServiceManager] Ended detail record {record.record_id} for room {service_obj.room_id}"
            )
        except Exception as e:
            logger.error(f"[ServiceManager] Failed to end detail record: {e}")

    def end_waiting_detail_record(self, wait_obj: WaitingObject):
        """结束等待对象的详单记录"""
        if not wait_obj.record_id:
            return

        try:
            record = ACDetailRecord.objects.get(record_id=wait_obj.record_id)
            record.end_time = timezone.now()
            record.end_temp = wait_obj.current_temp
            record.energy_consumed = wait_obj.energy_consumed
            record.cost = wait_obj.cost
            record.save()
            logger.info(
                f"[ServiceManager] Ended detail record {record.record_id} for waiting room {wait_obj.room_id}"
            )
        except Exception as e:
            logger.error(f"[ServiceManager] Failed to end waiting detail record: {e}")


# ============================================================
# ACScheduler（调度对象）- 只负责调度决策
# ============================================================


class ACScheduler:
    """
    调度对象 - 只负责调度决策，管理队列

    职责：
    1. 管理服务队列和等待队列
    2. 执行优先级调度（抢占调度）
    3. 执行时间片调度（轮转调度）
    4. 处理请求防抖

    不负责：
    - 温度计算（由 ServiceManager 处理）
    - 费用计算（由 ServiceManager 处理）
    - 详单记录（由 ServiceManager 处理）
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.service_queue: Dict[str, ServiceObject] = {}  # 服务队列
        self.wait_queue: Dict[str, WaitingObject] = {}  # 等待队列
        self.max_service_num = MAX_SERVICE_NUM
        self.wait_time_slice = WAIT_TIME_SLICE
        self.running = False
        self.scheduler_thread = None
        self._request_timestamps: Dict[str, float] = {}  # 记录请求时间戳，用于防抖
        self._pending_requests: Dict[str, dict] = {}  # 待处理的请求

        # 服务对象实例（负责实际操作）
        self.service_manager = ACServiceManager()

        logger.info(
            f"[Scheduler] ACScheduler initialized: max_service={self.max_service_num}, wait_slice={self.wait_time_slice}s"
        )

    def start(self):
        """启动调度器"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(
                target=self._scheduler_loop, daemon=True
            )
            self.scheduler_thread.start()
            logger.info("[Scheduler] ACScheduler started")

    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
        logger.info("[Scheduler] ACScheduler stopped")

    def _scheduler_loop(self):
        """调度器主循环"""
        while self.running:
            try:
                # 1. 处理待处理的请求（防抖）
                self._process_pending_requests()

                # 2. 委托 ServiceManager 更新温度和费用
                self._update_all_temperatures()

                # 3. 执行时间片调度
                self._check_wait_queue()

                # 4. 检查是否达到目标温度
                self._check_target_reached()

                time.sleep(1)  # 每秒执行一次
            except Exception as e:
                logger.error(f"[Scheduler] Scheduler loop error: {e}")

    def _process_pending_requests(self):
        """处理待处理的请求（防抖处理）"""
        current_time = time.time()
        to_process = []

        for room_id, timestamp in list(self._request_timestamps.items()):
            if current_time - timestamp >= 1.0:  # 超过1秒，处理请求
                if room_id in self._pending_requests:
                    to_process.append((room_id, self._pending_requests[room_id]))
                    del self._pending_requests[room_id]
                del self._request_timestamps[room_id]

        for room_id, request in to_process:
            self._handle_request(room_id, request)

    def _handle_request(self, room_id: str, request: dict):
        """实际处理请求 - 调度决策"""
        action = request.get("action")

        if action == "power_on":
            self._power_on(room_id, request)
        elif action == "power_off":
            self._power_off(room_id)
        elif action == "change_temp":
            self._change_temp(room_id, request)
        elif action == "change_speed":
            self._change_speed(room_id, request)

    def submit_request(self, room_id: str, request: dict):
        """提交请求（带防抖）"""
        current_time = time.time()

        # 如果是调温请求，不算新请求，直接处理
        if request.get("action") == "change_temp":
            self._handle_request(room_id, request)
            return {"status": "success", "message": "温度调节请求已处理"}

        # 其他请求需要防抖处理
        last_time = self._request_timestamps.get(room_id, 0)

        if current_time - last_time < 1.0:
            # 间隔小于1秒，覆盖之前的请求
            self._pending_requests[room_id] = request
            self._request_timestamps[room_id] = current_time
            return {"status": "pending", "message": "请求已更新，等待处理"}
        else:
            # 间隔大于1秒，直接处理
            self._request_timestamps[room_id] = current_time
            self._handle_request(room_id, request)
            return {"status": "success", "message": "请求已处理"}

    # ========== 调度决策方法 ==========

    def _power_on(self, room_id: str, request: dict):
        """开机请求 - 调度决策"""
        target_temp = request.get("target_temp", DEFAULT_TEMP)
        fan_speed = request.get("fan_speed", "medium")
        mode = request.get("mode", "cooling")

        # 验证温度范围
        if mode == "cooling":
            target_temp = max(COOLING_MIN_TEMP, min(COOLING_MAX_TEMP, target_temp))
        else:
            target_temp = max(HEATING_MIN_TEMP, min(HEATING_MAX_TEMP, target_temp))

        # 获取当前温度
        current_temp = self.service_manager.room_states.get(room_id, {}).get(
            "current_temp", INITIAL_ROOM_TEMP
        )

        # 调度决策：检查服务队列是否已满
        if len(self.service_queue) < self.max_service_num:
            # 直接分配服务
            self._allocate_service(room_id, target_temp, fan_speed, mode, current_temp)
            logger.info(f"[Scheduler] Room {room_id} started service directly")
        else:
            # 需要调度决策
            self._schedule_request(room_id, target_temp, fan_speed, mode, current_temp)

    def _schedule_request(
        self,
        room_id: str,
        target_temp: float,
        fan_speed: str,
        mode: str,
        current_temp: float,
    ):
        """调度新请求 - 优先级调度决策"""
        new_priority = FAN_SPEED_PRIORITY.get(fan_speed, 0)

        # 查找可以被抢占的服务对象
        preemptable = []
        for sid, sobj in self.service_queue.items():
            if sobj.get_priority() < new_priority:
                preemptable.append((sid, sobj))

        if preemptable:
            # 优先级调度：抢占低优先级的服务
            if len(preemptable) == 1:
                victim_id, victim = preemptable[0]
            else:
                # 多个可抢占，选择风速最低的；如果风速相同，选择服务时长最长的
                preemptable.sort(
                    key=lambda x: (x[1].get_priority(), -x[1].service_duration)
                )
                victim_id, victim = preemptable[0]

            # 将被抢占的房间放入等待队列
            self._move_to_wait_queue(victim_id, victim)

            # 新请求获得服务
            self._allocate_service(room_id, target_temp, fan_speed, mode, current_temp)
            logger.info(f"[Scheduler] Room {room_id} preempted room {victim_id}")
        else:
            # 时间片调度：加入等待队列
            self._add_to_wait_queue(room_id, target_temp, fan_speed, mode, current_temp)
            logger.info(f"[Scheduler] Room {room_id} added to wait queue")

    def _allocate_service(
        self,
        room_id: str,
        target_temp: float,
        fan_speed: str,
        mode: str,
        current_temp: float,
    ):
        """分配服务 - 创建服务对象"""
        service_obj = ServiceObject(room_id, target_temp, fan_speed, mode)
        service_obj.current_temp = current_temp
        self.service_queue[room_id] = service_obj

        # 委托 ServiceManager 创建详单记录
        self.service_manager.create_detail_record(service_obj)

        # 更新房间状态
        self.service_manager.update_room_status(
            room_id, "on", target_temp=target_temp, fan_speed=fan_speed, mode=mode
        )

    def _add_to_wait_queue(
        self,
        room_id: str,
        target_temp: float,
        fan_speed: str,
        mode: str,
        current_temp: float,
    ):
        """加入等待队列"""
        wait_obj = WaitingObject(room_id, target_temp, fan_speed, mode)
        wait_obj.current_temp = current_temp
        self.wait_queue[room_id] = wait_obj

        # 更新房间状态
        self.service_manager.update_room_status(
            room_id, "waiting", target_temp=target_temp, fan_speed=fan_speed, mode=mode
        )

    def _move_to_wait_queue(self, room_id: str, service_obj: ServiceObject):
        """将服务对象移动到等待队列"""
        # 委托 ServiceManager 结束详单记录
        self.service_manager.end_detail_record(service_obj)

        # 创建等待对象
        wait_obj = WaitingObject(
            room_id, service_obj.target_temp, service_obj.fan_speed, service_obj.mode
        )
        wait_obj.current_temp = service_obj.current_temp
        wait_obj.energy_consumed = service_obj.energy_consumed
        wait_obj.cost = service_obj.cost
        wait_obj.record_id = None  # 等待期间不关联详单

        self.wait_queue[room_id] = wait_obj
        del self.service_queue[room_id]

        # 更新房间状态
        self.service_manager.update_room_status(room_id, "waiting")
        logger.info(f"[Scheduler] Room {room_id} moved to wait queue")

    def _power_off(self, room_id: str):
        """关机请求 - 调度决策"""
        # 从服务队列移除
        if room_id in self.service_queue:
            # 委托 ServiceManager 结束详单记录
            self.service_manager.end_detail_record(self.service_queue[room_id])
            del self.service_queue[room_id]
            logger.info(f"[Scheduler] Room {room_id} removed from service queue")
            # 检查等待队列，分配空闲槽位
            self._allocate_from_wait_queue()

        # 从等待队列移除
        if room_id in self.wait_queue:
            wobj = self.wait_queue[room_id]
            if wobj.record_id:
                self.service_manager.end_waiting_detail_record(wobj)
            del self.wait_queue[room_id]
            logger.info(f"[Scheduler] Room {room_id} removed from wait queue")

        # 更新房间状态
        self.service_manager.update_room_status(room_id, "off")

    def _change_temp(self, room_id: str, request: dict):
        """调温请求（不算新请求，不触发调度）"""
        target_temp = request.get("target_temp")
        mode = request.get("mode", "cooling")

        # 验证温度范围
        if mode == "cooling":
            target_temp = max(COOLING_MIN_TEMP, min(COOLING_MAX_TEMP, target_temp))
        else:
            target_temp = max(HEATING_MIN_TEMP, min(HEATING_MAX_TEMP, target_temp))

        if room_id in self.service_queue:
            self.service_queue[room_id].target_temp = target_temp
            self.service_queue[room_id].mode = mode

        if room_id in self.wait_queue:
            self.wait_queue[room_id].target_temp = target_temp
            self.wait_queue[room_id].mode = mode

        # 更新房间状态
        if room_id in self.service_manager.room_states:
            self.service_manager.room_states[room_id]["target_temp"] = target_temp
            self.service_manager.room_states[room_id]["mode"] = mode

        logger.info(f"[Scheduler] Room {room_id} temperature changed to {target_temp}")

    def _change_speed(self, room_id: str, request: dict):
        """调风请求（算新请求，可能触发调度）"""
        new_speed = request.get("fan_speed", "medium")

        if room_id in self.service_queue:
            old_speed = self.service_queue[room_id].fan_speed

            # 委托 ServiceManager 结束旧记录
            self.service_manager.end_detail_record(self.service_queue[room_id])

            self.service_queue[room_id].fan_speed = new_speed
            self.service_queue[room_id].service_start_time = datetime.now()
            self.service_queue[room_id].service_duration = 0

            # 委托 ServiceManager 创建新记录
            self.service_manager.create_detail_record(self.service_queue[room_id])

            logger.info(
                f"[Scheduler] Room {room_id} speed changed from {old_speed} to {new_speed}"
            )

        elif room_id in self.wait_queue:
            self.wait_queue[room_id].fan_speed = new_speed
            # 检查是否可以抢占
            new_priority = FAN_SPEED_PRIORITY.get(new_speed, 0)
            for sid, sobj in list(self.service_queue.items()):
                if sobj.get_priority() < new_priority:
                    # 可以抢占
                    wait_obj = self.wait_queue[room_id]
                    self._move_to_wait_queue(sid, sobj)

                    # 分配服务
                    self._allocate_service(
                        room_id,
                        wait_obj.target_temp,
                        new_speed,
                        wait_obj.mode,
                        wait_obj.current_temp,
                    )
                    del self.wait_queue[room_id]

                    logger.info(
                        f"[Scheduler] Room {room_id} preempted room {sid} after speed change"
                    )
                    break

        # 更新房间状态
        if room_id in self.service_manager.room_states:
            self.service_manager.room_states[room_id]["fan_speed"] = new_speed

    # ========== 温度更新（委托给 ServiceManager）==========

    def _update_all_temperatures(self):
        """更新所有房间温度 - 委托给 ServiceManager"""
        # 更新服务中的房间
        for room_id, sobj in self.service_queue.items():
            self.service_manager.update_service_temperature(sobj)

        # 更新等待中的房间
        for room_id, wobj in self.wait_queue.items():
            self.service_manager.update_waiting_state(wobj)

        # 更新关机房间（回温）
        all_active = set(self.service_queue.keys()) | set(self.wait_queue.keys())
        for room_id in self.service_manager.room_states:
            if room_id not in all_active:
                self.service_manager.update_off_room_temperature(room_id)

    # ========== 时间片调度 ==========

    def _check_wait_queue(self):
        """检查等待队列，执行时间片调度"""
        if not self.wait_queue:
            return

        # 检查是否有等待时间到期的请求
        expired = []
        for room_id, wobj in self.wait_queue.items():
            if wobj.is_wait_expired():
                expired.append((room_id, wobj))
                wobj.waited_full_slice = True

        if expired and len(self.service_queue) >= self.max_service_num:
            # 按优先级和等待时间排序
            expired.sort(
                key=lambda x: (-x[1].get_priority(), x[1].waited_full_slice),
                reverse=True,
            )

            for room_id, wobj in expired:
                # 找到服务时长最长的同优先级或低优先级服务对象
                candidates = [
                    (sid, sobj)
                    for sid, sobj in self.service_queue.items()
                    if sobj.get_priority() <= wobj.get_priority()
                ]

                if candidates:
                    candidates.sort(key=lambda x: -x[1].service_duration)
                    victim_id, victim = candidates[0]

                    # 交换
                    self._move_to_wait_queue(victim_id, victim)

                    # 分配服务（继承等待期间的能耗和费用）
                    service_obj = ServiceObject(
                        room_id, wobj.target_temp, wobj.fan_speed, wobj.mode
                    )
                    service_obj.current_temp = wobj.current_temp
                    service_obj.energy_consumed = wobj.energy_consumed
                    service_obj.cost = wobj.cost
                    service_obj.record_id = wobj.record_id
                    self.service_queue[room_id] = service_obj
                    del self.wait_queue[room_id]

                    # 更新房间状态
                    self.service_manager.update_room_status(room_id, "on")
                    logger.info(
                        f"[Scheduler] Time slice: Room {room_id} replaced room {victim_id}"
                    )
                    break

    def _check_target_reached(self):
        """检查是否达到目标温度"""
        for room_id, sobj in list(self.service_queue.items()):
            if self.service_manager.check_target_reached(sobj):
                # 达到目标温度，进入待机状态
                self.service_manager.update_room_status(room_id, "standby")

                # 委托 ServiceManager 结束详单记录
                self.service_manager.end_detail_record(sobj)

                # 从服务队列移除，释放槽位
                del self.service_queue[room_id]
                logger.info(
                    f"[Scheduler] Room {room_id} reached target temperature, standby"
                )

                # 分配给等待队列
                self._allocate_from_wait_queue()

        # 检查待机房间是否需要重新启动
        for room_id in list(self.service_manager.room_states.keys()):
            if self.service_manager.check_need_restart(room_id):
                state = self.service_manager.room_states[room_id]
                self.submit_request(
                    room_id,
                    {
                        "action": "power_on",
                        "target_temp": state.get("target_temp", DEFAULT_TEMP),
                        "fan_speed": state.get("fan_speed", "medium"),
                        "mode": state.get("mode", "cooling"),
                    },
                )
                logger.info(
                    f"[Scheduler] Room {room_id} restarted due to temperature deviation"
                )

    def _allocate_from_wait_queue(self):
        """从等待队列分配服务"""
        while len(self.service_queue) < self.max_service_num and self.wait_queue:
            # 按优先级和等待时间选择
            candidates = list(self.wait_queue.items())
            candidates.sort(
                key=lambda x: (
                    -x[1].get_priority(),
                    x[1].waited_full_slice,
                    x[1].wait_start_time,
                )
            )

            room_id, wobj = candidates[0]

            # 分配服务（继承等待期间的能耗和费用）
            service_obj = ServiceObject(
                room_id, wobj.target_temp, wobj.fan_speed, wobj.mode
            )
            service_obj.current_temp = wobj.current_temp
            service_obj.energy_consumed = wobj.energy_consumed
            service_obj.cost = wobj.cost
            service_obj.record_id = wobj.record_id
            self.service_queue[room_id] = service_obj
            del self.wait_queue[room_id]

            # 更新房间状态
            self.service_manager.update_room_status(room_id, "on")
            logger.info(f"[Scheduler] Room {room_id} allocated from wait queue")

    # ========== 对外接口 ==========

    def get_room_state(self, room_id: str) -> dict:
        """获取房间状态"""
        if room_id in self.service_queue:
            sobj = self.service_queue[room_id]
            return {
                "room_id": room_id,
                "is_on": True,
                "status": "on",
                "current_temp": round(sobj.current_temp, 1),
                "target_temp": sobj.target_temp,
                "fan_speed": sobj.fan_speed,
                "mode": sobj.mode,
                "energy_consumed": round(sobj.energy_consumed, 2),
                "cost": float(sobj.cost),
                "service_duration": sobj.service_duration,
            }
        elif room_id in self.wait_queue:
            wobj = self.wait_queue[room_id]
            return {
                "room_id": room_id,
                "is_on": True,
                "status": "waiting",
                "current_temp": round(wobj.current_temp, 1),
                "target_temp": wobj.target_temp,
                "fan_speed": wobj.fan_speed,
                "mode": wobj.mode,
                "energy_consumed": round(wobj.energy_consumed, 2),
                "cost": float(wobj.cost),
                "remaining_wait": wobj.get_remaining_wait_time(),
            }
        else:
            return self.service_manager.get_room_state(room_id)

    def get_all_states(self) -> List[dict]:
        """获取所有房间状态（用于监控）"""
        all_rooms = (
            set(self.service_manager.room_states.keys())
            | set(self.service_queue.keys())
            | set(self.wait_queue.keys())
        )
        return [self.get_room_state(room_id) for room_id in all_rooms]

    def init_room(self, room_id: str):
        """初始化房间空调状态（入住时调用）"""
        self.service_manager.init_room(room_id)

    def checkout_room(self, room_id: str) -> dict:
        """退房时获取空调使用信息并清理"""
        state = self.get_room_state(room_id)

        # 关闭空调
        self._power_off(room_id)

        # 委托 ServiceManager 清理状态
        self.service_manager.clear_room(room_id)

        logger.info(
            f"[Scheduler] Room {room_id} checked out, AC cost: {state.get('cost', 0)}"
        )
        return state


# 全局调度器实例
scheduler = ACScheduler()
