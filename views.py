"""
API视图
"""

from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime

from .models import Room, Customer, AccommodationOrder, ACState, AccommodationBill
from .serializers import (
    RoomSerializer,
    AccommodationOrderSerializer,
    ACStateSerializer,
    AccommodationBillSerializer,
    CheckInRequestSerializer,
    CheckOutRequestSerializer,
    ACControlRequestSerializer,
)
from .services import CheckInService, CheckOutService, ACService, ReportService


class RoomListView(APIView):
    """房间列表（包含入住信息）"""

    def get(self, request):
        rooms = Room.objects.all()
        data = []
        for room in rooms:
            room_data = {
                "room_id": room.room_id,
                "room_type": room.room_type,
                "room_type_display": room.get_room_type_display(),
                "status": room.status,
                "status_display": room.get_status_display(),
                "price_per_day": float(room.price_per_day),
                "is_occupied": room.status == "occupied",
                "guest": None,
            }
            # 如果已入住，获取客人信息
            if room.status == "occupied":
                active_order = AccommodationOrder.objects.filter(
                    room=room, status="active"
                ).first()
                if active_order:
                    room_data["guest"] = {
                        "name": active_order.customer.name,
                        "phone": active_order.customer.phone,
                        "id_card": active_order.customer.id_card,
                        "check_in_time": active_order.check_in_time.isoformat(),
                    }
            data.append(room_data)
        return Response({"code": 200, "data": data, "message": "success"})


class AvailableRoomListView(APIView):
    """可用房间列表"""

    def get(self, request):
        rooms = Room.objects.filter(status="available")
        print(f"Available rooms count: {rooms.count()}")  # Debug log
        serializer = RoomSerializer(rooms, many=True)
        return Response({"code": 200, "data": serializer.data, "message": "success"})


class CheckInView(APIView):
    """办理入住"""

    def post(self, request):
        serializer = CheckInRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"code": 400, "data": None, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        # 验证顾客
        success, msg, customer = CheckInService.validate_customer(
            data["name"], data["id_card"], data["phone"]
        )
        if not success:
            return Response(
                {"code": 400, "data": None, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证房间
        success, msg, room = CheckInService.validate_room(data["room_id"])
        if not success:
            return Response(
                {"code": 400, "data": None, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 创建订单
        try:
            order = CheckInService.create_order(
                customer, room, data.get("check_in_date"), data.get("check_out_date")
            )

            return Response(
                {
                    "code": 200,
                    "data": {
                        "order_id": order.order_id,
                        "room_id": order.room_id,
                        "customer_name": customer.name,
                        "check_in_time": order.check_in_time.strftime("%Y-%m-%d %H:%M"),
                        "room_type": room.get_room_type_display(),
                        "room_fee": float(order.room_fee),
                    },
                    "message": "入住成功",
                }
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            return Response(
                {"code": 500, "data": None, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CheckOutView(APIView):
    """办理结账"""

    def post(self, request):
        serializer = CheckOutRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"code": 400, "data": None, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room_id = serializer.validated_data["room_id"]

        success, msg, bill_data = CheckOutService.checkout(room_id)

        if success:
            return Response({"code": 200, "data": bill_data, "message": msg})
        else:
            return Response(
                {"code": 400, "data": None, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PayBillView(APIView):
    """支付账单"""

    def post(self, request):
        bill_id = request.data.get("bill_id")
        if not bill_id:
            return Response(
                {"code": 400, "data": None, "message": "缺少账单ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, msg = CheckOutService.pay_bill(bill_id)

        if success:
            return Response({"code": 200, "data": None, "message": msg})
        else:
            return Response(
                {"code": 400, "data": None, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )


class BillDetailView(APIView):
    """获取账单详情"""

    def get(self, request, room_id):
        success, msg, order = CheckOutService.get_active_order(room_id)
        if not success:
            return Response(
                {"code": 400, "data": None, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room_fee = CheckOutService.calculate_room_fee(order)
        from .models import ACDetailRecord
        ac_fee = sum(Decimal(str(r.cost or 0)) for r in ACDetailRecord.objects.filter(order=order))

        return Response(
            {
                "code": 200,
                "data": {
                    "room_id": room_id,
                    "customer_name": order.customer.name,
                    "check_in_time": order.check_in_time.strftime("%Y-%m-%d %H:%M"),
                    "room_fee": round(float(room_fee), 2),
                    "ac_fee": round(float(ac_fee), 2),
                    "total_fee": round(float(room_fee + ac_fee), 2),
                },
                "message": "success",
            }
        )


class ACControlView(APIView):
    """空调控制"""

    def post(self, request):
        serializer = ACControlRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"code": 400, "data": None, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        room_id = data["room_id"]
        action = data["action"]

        try:
            if action == "power_on":
                result = ACService.power_on(
                    room_id,
                    data.get("target_temp", 25),
                    data.get("fan_speed", "medium"),
                    data.get("mode", "cooling"),
                )
            elif action == "power_off":
                result = ACService.power_off(room_id)
            elif action == "change_temp":
                result = ACService.change_temp(
                    room_id, data.get("target_temp", 25), data.get("mode", "cooling")
                )
            elif action == "change_speed":
                result = ACService.change_speed(
                    room_id, data.get("fan_speed", "medium")
                )
            else:
                return Response(
                    {"code": 400, "data": None, "message": "未知操作"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 获取最新状态
            state = ACService.get_state(room_id)

            return Response(
                {
                    "code": 200,
                    "data": state,
                    "message": result.get("message", "success"),
                }
            )
        except Exception as e:
            return Response(
                {"code": 500, "data": None, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ACStateView(APIView):
    """获取空调状态"""

    def get(self, request, room_id):
        state = ACService.get_state(room_id)
        return Response({"code": 200, "data": state, "message": "success"})


class ACMonitorView(APIView):
    """空调监控（管理员用）"""

    def get(self, request):
        states = ACService.get_all_states()
        return Response({"code": 200, "data": states, "message": "success"})

class ACDetailListView(APIView):
    """获取当前入住的空调运行详单"""

    def get(self, request, room_id):
        success, msg, order = CheckOutService.get_active_order(room_id)
        if not success or not order:
            return Response(
                {"code": 400, "data": None, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from .models import ACDetailRecord

        records = ACDetailRecord.objects.filter(order=order).order_by("start_time")

        total_energy = 0.0
        total_cost = Decimal("0.00")
        total_seconds = 0
        details = []

        for idx, r in enumerate(records, start=1):
            start = r.start_time
            end = r.end_time or timezone.now()
            duration_seconds = int((end - start).total_seconds())

            energy = round(float(r.energy_consumed or 0), 2)
            cost = Decimal(str(r.cost or 0))

            total_energy += energy
            total_cost += cost
            total_seconds += duration_seconds

            details.append(
                {
                    "seq": idx,
                    "start_time": start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": r.end_time and r.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_seconds": duration_seconds,
                    "start_temp": round(float(r.start_temp), 2),
                    "end_temp": None if r.end_temp is None else round(float(r.end_temp), 2),
                    "target_temp": round(float(r.target_temp), 2),
                    "fan_speed": r.fan_speed,
                    "mode": r.mode,
                    "energy": energy,
                    "cost": round(float(cost), 2),
                }
            )

        data = {
            "room_id": room_id,
            "order_id": order.order_id,
            "summary": {
                "total_records": len(details),
                "total_duration_seconds": total_seconds,
                "total_energy": round(float(total_energy), 2),
                "total_cost": round(float(total_cost), 2),
            },
            "details": details,
        }

        return Response({"code": 200, "data": data, "message": "success"})


class OrderListView(APIView):
    """订单列表"""

    def get(self, request):
        status_filter = request.query_params.get("status", None)

        orders = AccommodationOrder.objects.all().order_by("-check_in_time")
        if status_filter:
            orders = orders.filter(status=status_filter)

        serializer = AccommodationOrderSerializer(orders, many=True)
        return Response({"code": 200, "data": serializer.data, "message": "success"})


class ReportView(APIView):
    """统计报表"""

    def get(self, request):
        report_type = request.query_params.get("type", "daily")
        date_str = request.query_params.get("date", None)

        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                date = timezone.now().date()
        else:
            date = timezone.now().date()

        if report_type == "daily":
            report = ReportService.generate_daily_report(date)
        else:
            report = ReportService.generate_daily_report(date)

        return Response({"code": 200, "data": report, "message": "success"})
