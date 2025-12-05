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
    # 空调控制相关
    path("ac/control/", views.ACControlView.as_view(), name="ac-control"),
    path("ac/state/<str:room_id>/", views.ACStateView.as_view(), name="ac-state"),
    path("ac/monitor/", views.ACMonitorView.as_view(), name="ac-monitor"),
    # 订单和报表
    path("orders/", views.OrderListView.as_view(), name="order-list"),
    path("report/", views.ReportView.as_view(), name="report"),
]
