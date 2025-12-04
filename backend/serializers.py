"""
序列化器
"""

from rest_framework import serializers
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


class RoomSerializer(serializers.ModelSerializer):
    room_type_display = serializers.CharField(
        source="get_room_type_display", read_only=True
    )

    class Meta:
        model = Room
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class AccommodationOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    room_type = serializers.CharField(
        source="room.get_room_type_display", read_only=True
    )

    class Meta:
        model = AccommodationOrder
        fields = "__all__"


class ACStateSerializer(serializers.ModelSerializer):
    room_id = serializers.CharField(source="room.room_id", read_only=True)
    mode_display = serializers.CharField(source="get_mode_display", read_only=True)
    fan_speed_display = serializers.CharField(
        source="get_fan_speed_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ACState
        fields = "__all__"


class ACDetailRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ACDetailRecord
        fields = "__all__"


class ACBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ACBill
        fields = "__all__"


class AccommodationBillSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="order.customer.name", read_only=True)
    room_id = serializers.CharField(source="order.room.room_id", read_only=True)

    class Meta:
        model = AccommodationBill
        fields = "__all__"


class CheckInRequestSerializer(serializers.Serializer):
    """入住请求序列化器"""

    name = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=11)
    id_card = serializers.CharField(max_length=18)
    room_id = serializers.CharField(max_length=10)
    check_in_date = serializers.DateTimeField(required=False)
    check_out_date = serializers.DateTimeField(required=False)


class CheckOutRequestSerializer(serializers.Serializer):
    """结账请求序列化器"""

    room_id = serializers.CharField(max_length=10)


class ACControlRequestSerializer(serializers.Serializer):
    """空调控制请求序列化器"""

    room_id = serializers.CharField(max_length=10)
    action = serializers.ChoiceField(
        choices=["power_on", "power_off", "change_temp", "change_speed"]
    )
    target_temp = serializers.FloatField(required=False)
    fan_speed = serializers.ChoiceField(
        choices=["low", "medium", "high"], required=False
    )
    mode = serializers.ChoiceField(choices=["cooling", "heating"], required=False)
