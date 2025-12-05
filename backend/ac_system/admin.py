"""
Django admin配置
"""

from django.contrib import admin
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


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["room_id", "room_type", "status", "price_per_day"]
    list_filter = ["room_type", "status"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["customer_id", "name", "phone", "id_card"]
    search_fields = ["name", "phone", "id_card"]


@admin.register(AccommodationOrder)
class AccommodationOrderAdmin(admin.ModelAdmin):
    list_display = ["order_id", "customer", "room", "check_in_time", "status"]
    list_filter = ["status"]


@admin.register(ACState)
class ACStateAdmin(admin.ModelAdmin):
    list_display = [
        "room",
        "is_on",
        "status",
        "current_temp",
        "target_temp",
        "fan_speed",
    ]


@admin.register(ACDetailRecord)
class ACDetailRecordAdmin(admin.ModelAdmin):
    list_display = ["record_id", "room", "start_time", "end_time", "fan_speed", "cost"]


@admin.register(ACBill)
class ACBillAdmin(admin.ModelAdmin):
    list_display = ["bill_id", "room", "total_energy", "total_cost"]


@admin.register(AccommodationBill)
class AccommodationBillAdmin(admin.ModelAdmin):
    list_display = ["bill_id", "order", "room_fee", "ac_fee", "total_fee", "is_paid"]


@admin.register(StatisticsReport)
class StatisticsReportAdmin(admin.ModelAdmin):
    list_display = ["report_id", "report_type", "start_date", "end_date"]
