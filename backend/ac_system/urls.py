"""
URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 房间相关
    path("rooms/", views.RoomListView.as_view(), name="room-list"),
    path(
        "rooms/available/",
        views.AvailableRoomListView.as_view(),
        name="available-rooms",
    ),
    # 入住/结账相关
    path("checkin/", views.CheckInView.as_view(), name="check-in"),
    path("checkout/", views.CheckOutView.as_view(), name="check-out"),
    path("bill/<str:room_id>/", views.BillDetailView.as_view(), name="bill-detail"),
    path("pay/", views.PayBillView.as_view(), name="pay-bill"),
    path("meal/order/", views.MealOrderView.as_view(), name="meal-order"),
    path(
        "meal/orders/<str:room_id>/",
        views.MealOrderListView.as_view(),
        name="meal-orders",
    ),
    path("reserve/", views.ReservationView.as_view(), name="reserve-room"),
    # 空调控制相关
    path("ac/control/", views.ACControlView.as_view(), name="ac-control"),
    path("ac/state/<str:room_id>/", views.ACStateView.as_view(), name="ac-state"),
    path("ac/monitor/", views.ACMonitorView.as_view(), name="ac-monitor"),
    path(
        "ac/details/<str:room_id>/", views.ACDetailListView.as_view(), name="ac-details"
    ),
    # 订单和报表
    path("orders/", views.OrderListView.as_view(), name="order-list"),
    path("report/", views.ReportView.as_view(), name="report"),
    path("manager-report/", views.ManagerReportView.as_view(), name="manager-report"),
    # 测试日志
    path("test/log/", views.TestLogView.as_view(), name="test-log"),
    path(
        "admin/room/<str:room_id>/init/",
        views.AdminInitView.as_view(),
        name="admin-init",
    ),
    path(
        "admin/room/<str:room_id>/clear/",
        views.AdminClearView.as_view(),
        name="admin-clear",
    ),
]
