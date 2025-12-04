"""
数据模型定义
"""

from django.db import models
from django.utils import timezone


class Room(models.Model):
    """房间模型"""

    ROOM_TYPE_CHOICES = [
        ("standard", "标准间"),
        ("deluxe", "豪华间"),
        ("suite", "套房"),
    ]

    STATUS_CHOICES = [
        ("available", "空闲"),
        ("occupied", "已入住"),
        ("maintenance", "维护中"),
    ]

    room_id = models.CharField(max_length=10, primary_key=True, verbose_name="房间号")
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default="standard",
        verbose_name="房间类型",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available",
        verbose_name="房间状态",
    )
    price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2, default=400, verbose_name="每日房价"
    )

    class Meta:
        db_table = "room"
        verbose_name = "房间"
        verbose_name_plural = "房间"

    def __str__(self):
        return f"房间 {self.room_id}"

    def is_available(self):
        return self.status == "available"

    def set_occupied(self):
        self.status = "occupied"
        self.save()

    def set_available(self):
        self.status = "available"
        self.save()


class Customer(models.Model):
    """顾客模型"""

    customer_id = models.AutoField(primary_key=True, verbose_name="顾客ID")
    name = models.CharField(max_length=50, verbose_name="姓名")
    id_card = models.CharField(max_length=18, verbose_name="身份证号")
    phone = models.CharField(max_length=11, verbose_name="手机号")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "customer"
        verbose_name = "顾客"
        verbose_name_plural = "顾客"

    def __str__(self):
        return f"{self.name}"


class AccommodationOrder(models.Model):
    """入住订单模型"""

    STATUS_CHOICES = [
        ("active", "入住中"),
        ("completed", "已退房"),
        ("cancelled", "已取消"),
    ]

    order_id = models.AutoField(primary_key=True, verbose_name="订单ID")
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name="顾客"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="房间")
    check_in_time = models.DateTimeField(default=timezone.now, verbose_name="入住时间")
    check_out_time = models.DateTimeField(
        null=True, blank=True, verbose_name="退房时间"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="订单状态"
    )
    room_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="房费"
    )

    class Meta:
        db_table = "accommodation_order"
        verbose_name = "入住订单"
        verbose_name_plural = "入住订单"

    def __str__(self):
        return f"订单 {self.order_id} - {self.customer.name}"


class ACState(models.Model):
    """空调状态模型"""

    MODE_CHOICES = [
        ("cooling", "制冷"),
        ("heating", "制热"),
    ]

    FAN_SPEED_CHOICES = [
        ("low", "低风"),
        ("medium", "中风"),
        ("high", "高风"),
    ]

    STATUS_CHOICES = [
        ("off", "关机"),
        ("on", "开机"),
        ("standby", "待机"),  # 达到目标温度后待机
    ]

    room = models.OneToOneField(
        Room, on_delete=models.CASCADE, primary_key=True, verbose_name="房间"
    )
    is_on = models.BooleanField(default=False, verbose_name="是否开机")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="off", verbose_name="空调状态"
    )
    mode = models.CharField(
        max_length=20, choices=MODE_CHOICES, default="cooling", verbose_name="模式"
    )
    current_temp = models.FloatField(default=25.0, verbose_name="当前温度")
    target_temp = models.FloatField(default=25.0, verbose_name="目标温度")
    fan_speed = models.CharField(
        max_length=10, choices=FAN_SPEED_CHOICES, default="medium", verbose_name="风速"
    )
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="累计费用"
    )
    total_energy = models.FloatField(default=0, verbose_name="累计耗电量(度)")
    service_start_time = models.DateTimeField(
        null=True, blank=True, verbose_name="服务开始时间"
    )
    last_update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")

    class Meta:
        db_table = "ac_state"
        verbose_name = "空调状态"
        verbose_name_plural = "空调状态"

    def __str__(self):
        return f"房间 {self.room_id} 空调状态"


class ACDetailRecord(models.Model):
    """空调使用详单模型"""

    record_id = models.AutoField(primary_key=True, verbose_name="详单ID")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="房间")
    order = models.ForeignKey(
        AccommodationOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="关联订单",
    )
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    start_temp = models.FloatField(verbose_name="开始温度")
    end_temp = models.FloatField(null=True, blank=True, verbose_name="结束温度")
    target_temp = models.FloatField(verbose_name="目标温度")
    fan_speed = models.CharField(max_length=10, verbose_name="风速")
    mode = models.CharField(max_length=20, verbose_name="模式")
    energy_consumed = models.FloatField(default=0, verbose_name="耗电量(度)")
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="费用"
    )

    class Meta:
        db_table = "ac_detail_record"
        verbose_name = "空调使用详单"
        verbose_name_plural = "空调使用详单"

    def __str__(self):
        return f"详单 {self.record_id} - 房间 {self.room_id}"


class ACBill(models.Model):
    """空调使用费账单模型"""

    bill_id = models.AutoField(primary_key=True, verbose_name="账单ID")
    order = models.ForeignKey(
        AccommodationOrder, on_delete=models.CASCADE, verbose_name="关联订单"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="房间")
    total_energy = models.FloatField(default=0, verbose_name="总耗电量(度)")
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="总费用"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "ac_bill"
        verbose_name = "空调账单"
        verbose_name_plural = "空调账单"

    def __str__(self):
        return f"空调账单 {self.bill_id} - 房间 {self.room_id}"


class AccommodationBill(models.Model):
    """住宿总账单模型"""

    bill_id = models.AutoField(primary_key=True, verbose_name="账单ID")
    order = models.OneToOneField(
        AccommodationOrder, on_delete=models.CASCADE, verbose_name="关联订单"
    )
    room_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="房费"
    )
    ac_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="空调费"
    )
    total_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="总费用"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_paid = models.BooleanField(default=False, verbose_name="是否已支付")

    class Meta:
        db_table = "accommodation_bill"
        verbose_name = "住宿账单"
        verbose_name_plural = "住宿账单"

    def __str__(self):
        return f"住宿账单 {self.bill_id}"


class StatisticsReport(models.Model):
    """统计报表模型"""

    REPORT_TYPE_CHOICES = [
        ("daily", "日报表"),
        ("weekly", "周报表"),
        ("monthly", "月报表"),
    ]

    report_id = models.AutoField(primary_key=True, verbose_name="报表ID")
    report_type = models.CharField(
        max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name="报表类型"
    )
    start_date = models.DateField(verbose_name="开始日期")
    end_date = models.DateField(verbose_name="结束日期")
    total_rooms_used = models.IntegerField(default=0, verbose_name="使用房间数")
    total_energy = models.FloatField(default=0, verbose_name="总耗电量(度)")
    total_ac_income = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="空调收入"
    )
    total_room_income = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="房费收入"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "statistics_report"
        verbose_name = "统计报表"
        verbose_name_plural = "统计报表"

    def __str__(self):
        return f"{self.get_report_type_display()} {self.start_date} - {self.end_date}"
