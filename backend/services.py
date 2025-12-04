"""
业务服务层
"""

from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from typing import Optional, Tuple, List

from .models import (
    Room,
    Customer,
    AccommodationOrder,
    ACState,
    ACDetailRecord,
    ACBill,
    AccommodationBill,
    StatisticsReport,
)
from .scheduler import scheduler
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ROOM_PRICE, DEFAULT_TEMP


class CheckInService:
    """入住服务"""

    @staticmethod
    def validate_customer(
        name: str, id_card: str, phone: str
    ) -> Tuple[bool, str, Optional[Customer]]:
        """验证顾客信息"""
        if not name or not id_card or not phone:
            return False, "顾客信息不完整", None

        # 检查是否已有未退房的订单
        existing_order = AccommodationOrder.objects.filter(
            customer__id_card=id_card, status="active"
        ).first()

        if existing_order:
            return False, f"该顾客已入住房间 {existing_order.room_id}", None

        # 获取或创建顾客
        customer, created = Customer.objects.get_or_create(
            id_card=id_card, defaults={"name": name, "phone": phone}
        )

        if not created:
            customer.name = name
            customer.phone = phone
            customer.save()

        return True, "验证通过", customer

    @staticmethod
    def validate_room(room_id: str) -> Tuple[bool, str, Optional[Room]]:
        """验证房间是否可用"""
        try:
            room = Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            return False, "房间不存在", None

        if not room.is_available():
            return False, "房间已被占用", None

        return True, "房间可用", room

    @staticmethod
    @transaction.atomic
    def create_order(
        customer: Customer,
        room: Room,
        check_in_date: datetime = None,
        check_out_date: datetime = None,
    ) -> AccommodationOrder:
        """创建入住订单"""
        if check_in_date is None:
            check_in_date = timezone.now()

        # 计算房费
        days = 1
        if check_out_date:
            days = max(1, (check_out_date - check_in_date).days)
        room_fee = room.price_per_day * days

        # 创建订单
        order = AccommodationOrder.objects.create(
            customer=customer,
            room=room,
            check_in_time=check_in_date,
            status="active",
            room_fee=room_fee,
        )

        # 更新房间状态
        room.set_occupied()

        # 初始化空调状态
        ACState.objects.update_or_create(
            room=room,
            defaults={
                "is_on": False,
                "status": "off",
                "mode": "cooling",
                "current_temp": 28.0,
                "target_temp": DEFAULT_TEMP,
                "fan_speed": "medium",
                "total_cost": 0,
                "total_energy": 0,
                "service_start_time": None,
            },
        )

        # 在调度器中初始化房间
        scheduler.init_room(room.room_id)

        return order


class CheckOutService:
    """结账服务"""

    @staticmethod
    def get_active_order(
        room_id: str,
    ) -> Tuple[bool, str, Optional[AccommodationOrder]]:
        """获取房间的活跃订单"""
        try:
            order = AccommodationOrder.objects.get(room_id=room_id, status="active")
            return True, "找到订单", order
        except AccommodationOrder.DoesNotExist:
            return False, "该房间没有入住记录", None

    @staticmethod
    def calculate_room_fee(order: AccommodationOrder) -> Decimal:
        """计算房费"""
        check_out_time = timezone.now()
        days = max(1, (check_out_time - order.check_in_time).days + 1)
        return order.room.price_per_day * days

    @staticmethod
    def calculate_ac_fee(room_id: str, order: AccommodationOrder) -> Decimal:
        """计算空调费"""
        # 从调度器获取实时费用
        ac_state = scheduler.checkout_room(room_id)
        return Decimal(str(ac_state.get("cost", 0)))

    @staticmethod
    @transaction.atomic
    def create_bill(order: AccommodationOrder) -> AccommodationBill:
        """创建总账单"""
        room_id = order.room_id

        # 计算房费
        room_fee = CheckOutService.calculate_room_fee(order)

        # 计算空调费
        ac_fee = CheckOutService.calculate_ac_fee(room_id, order)

        # 创建空调账单
        ac_bill = ACBill.objects.create(
            order=order,
            room_id=room_id,
            total_energy=0,  # TODO: 从详单汇总
            total_cost=ac_fee,
        )

        # 创建总账单
        total_fee = room_fee + ac_fee
        bill = AccommodationBill.objects.create(
            order=order, room_fee=room_fee, ac_fee=ac_fee, total_fee=total_fee
        )

        return bill

    @staticmethod
    @transaction.atomic
    def checkout(room_id: str) -> Tuple[bool, str, Optional[dict]]:
        """办理退房"""
        success, msg, order = CheckOutService.get_active_order(room_id)
        if not success:
            return False, msg, None

        # 创建账单
        bill = CheckOutService.create_bill(order)

        # 更新订单状态
        order.check_out_time = timezone.now()
        order.status = "completed"
        order.save()

        # 更新房间状态
        order.room.set_available()

        return (
            True,
            "结账成功",
            {
                "bill_id": bill.bill_id,
                "room_id": room_id,
                "customer_name": order.customer.name,
                "check_in_time": order.check_in_time.strftime("%Y-%m-%d %H:%M"),
                "check_out_time": order.check_out_time.strftime("%Y-%m-%d %H:%M"),
                "room_fee": round(float(bill.room_fee), 2),
                "ac_fee": round(float(bill.ac_fee), 2),
                "total_fee": round(float(bill.total_fee), 2),
            },
        )

    @staticmethod
    def pay_bill(bill_id: int) -> Tuple[bool, str]:
        """支付账单"""
        try:
            bill = AccommodationBill.objects.get(bill_id=bill_id)
            bill.is_paid = True
            bill.save()
            return True, "支付成功"
        except AccommodationBill.DoesNotExist:
            return False, "账单不存在"


class ACService:
    """空调服务"""

    @staticmethod
    def power_on(room_id: str, target_temp: float, fan_speed: str, mode: str) -> dict:
        """开机"""
        result = scheduler.submit_request(
            room_id,
            {
                "action": "power_on",
                "target_temp": target_temp,
                "fan_speed": fan_speed,
                "mode": mode,
            },
        )

        # 更新数据库状态
        ACService._update_db_state(room_id)

        return result

    @staticmethod
    def power_off(room_id: str) -> dict:
        """关机"""
        result = scheduler.submit_request(room_id, {"action": "power_off"})

        # 更新数据库状态
        ACService._update_db_state(room_id)

        return result

    @staticmethod
    def change_temp(room_id: str, target_temp: float, mode: str) -> dict:
        """调温"""
        result = scheduler.submit_request(
            room_id, {"action": "change_temp", "target_temp": target_temp, "mode": mode}
        )

        ACService._update_db_state(room_id)
        return result

    @staticmethod
    def change_speed(room_id: str, fan_speed: str) -> dict:
        """调风速"""
        result = scheduler.submit_request(
            room_id, {"action": "change_speed", "fan_speed": fan_speed}
        )

        ACService._update_db_state(room_id)
        return result

    @staticmethod
    def get_state(room_id: str) -> dict:
        """获取空调状态"""
        return scheduler.get_room_state(room_id)

    @staticmethod
    def get_all_states() -> List[dict]:
        """获取所有房间空调状态（监控用）"""
        return scheduler.get_all_states()

    @staticmethod
    def _update_db_state(room_id: str):
        """更新数据库中的空调状态"""
        state = scheduler.get_room_state(room_id)
        try:
            ac_state = ACState.objects.get(room_id=room_id)
            ac_state.is_on = state.get("is_on", False)
            ac_state.status = state.get("status", "off")
            ac_state.mode = state.get("mode", "cooling")
            ac_state.current_temp = state.get("current_temp", 25)
            ac_state.target_temp = state.get("target_temp", 25)
            ac_state.fan_speed = state.get("fan_speed", "medium")
            ac_state.total_cost = Decimal(str(state.get("cost", 0)))
            ac_state.total_energy = state.get("energy_consumed", 0)
            ac_state.save()
        except ACState.DoesNotExist:
            pass


class ReportService:
    """报表服务"""

    @staticmethod
    def generate_daily_report(date: datetime.date) -> dict:
        """生成日报表"""
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())

        orders = AccommodationOrder.objects.filter(check_in_time__range=(start, end))

        bills = AccommodationBill.objects.filter(created_at__range=(start, end))

        total_room_income = sum(b.room_fee for b in bills)
        total_ac_income = sum(b.ac_fee for b in bills)

        return {
            "report_type": "daily",
            "date": date.strftime("%Y-%m-%d"),
            "total_checkins": orders.count(),
            "total_room_income": float(total_room_income),
            "total_ac_income": float(total_ac_income),
            "total_income": float(total_room_income + total_ac_income),
        }

    @staticmethod
    def get_room_usage_stats(
        start_date: datetime.date, end_date: datetime.date
    ) -> List[dict]:
        """获取房间使用统计"""
        records = (
            ACDetailRecord.objects.filter(
                start_time__date__gte=start_date, start_time__date__lte=end_date
            )
            .values("room_id")
            .annotate(
                total_energy=models.Sum("energy_consumed"),
                total_cost=models.Sum("cost"),
                usage_count=models.Count("record_id"),
            )
        )

        return list(records)
