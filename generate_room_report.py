"""
房间空调详细记录报告生成器

功能：
- 读取数据库中的空调详单记录 (ACDetailRecord)
- 为每个房间生成详细的空调使用报告
- 支持输出到控制台和文件
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

# 设置 Django 环境
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_ac.settings")

import django
django.setup()

from ac_system.models import Room, ACDetailRecord, AccommodationOrder


def generate_room_report(room_id: str) -> dict:
    """
    生成单个房间的详细空调报告
    
    返回：包含房间统计信息的字典
    """
    records = ACDetailRecord.objects.filter(room_id=room_id).order_by('start_time')
    
    if not records.exists():
        return {
            "room_id": room_id,
            "total_records": 0,
            "total_cost": Decimal("0.00"),
            "total_energy": 0.0,
            "total_duration": 0,
            "records": []
        }
    
    total_cost = Decimal("0.00")
    total_energy = 0.0
    total_duration = 0
    record_list = []
    
    for idx, record in enumerate(records, 1):
        # 计算服务时长
        duration = 0
        if record.start_time and record.end_time:
            duration = (record.end_time - record.start_time).total_seconds()
        
        # 累计统计
        if record.cost:
            total_cost += record.cost
        if record.energy_consumed:
            total_energy += record.energy_consumed
        total_duration += duration
        
        record_list.append({
            "idx": idx,
            "start_time": record.start_time,
            "end_time": record.end_time,
            "duration": duration,
            "start_temp": record.start_temp,
            "end_temp": record.end_temp,
            "target_temp": record.target_temp,
            "fan_speed": record.fan_speed,
            "mode": record.mode,
            "energy_consumed": record.energy_consumed or 0,
            "cost": record.cost or Decimal("0.00"),
        })
    
    return {
        "room_id": room_id,
        "total_records": len(record_list),
        "total_cost": total_cost,
        "total_energy": total_energy,
        "total_duration": total_duration,
        "records": record_list
    }


def format_duration(seconds: float) -> str:
    """格式化时长为可读字符串"""
    if seconds < 60:
        return f"{seconds:.0f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}小时"


def print_room_report(report: dict):
    """打印单个房间的详细报告"""
    room_id = report["room_id"]
    
    print(f"\n{'='*80}")
    print(f"房间 {room_id} - 空调使用详细记录")
    print(f"{'='*80}")
    
    if report["total_records"] == 0:
        print("  暂无空调使用记录")
        return
    
    # 汇总信息
    print(f"\n【汇总统计】")
    print(f"  总服务次数: {report['total_records']} 次")
    print(f"  总服务时长: {format_duration(report['total_duration'])}")
    print(f"  总能耗: {report['total_energy']:.4f} 度")
    print(f"  总费用: {report['total_cost']:.2f} 元")
    
    # 详单列表
    print(f"\n【详单记录】")
    print("-" * 100)
    print(f"  {'序号':<6} {'开始时间':<12} {'结束时间':<12} {'时长':<10} {'起始温度':<10} {'结束温度':<10} {'目标温度':<10} {'风速':<8} {'费用':<10}")
    print("-" * 100)
    
    for idx, record in enumerate(report["records"], 1):
        start_time = record["start_time"].strftime("%H:%M:%S") if record["start_time"] else "-"
        end_time = record["end_time"].strftime("%H:%M:%S") if record["end_time"] else "进行中"
        duration = format_duration(record["duration"]) if record["duration"] > 0 else "-"
        start_temp = f"{record['start_temp']:.1f}°C" if record["start_temp"] is not None else "-"
        end_temp = f"{record['end_temp']:.1f}°C" if record["end_temp"] is not None else "-"
        target_temp = f"{record['target_temp']:.1f}°C" if record["target_temp"] is not None else "-"
        fan_speed = record["fan_speed"] or "-"
        cost = f"{record['cost']:.2f}元" if record["cost"] else "-"
        
        # 风速中文显示
        fan_speed_cn = {"high": "高", "medium": "中", "low": "低"}.get(fan_speed, fan_speed)
        
        print(f"  {idx:<6} {start_time:<12} {end_time:<12} {duration:<10} {start_temp:<10} {end_temp:<10} {target_temp:<10} {fan_speed_cn:<8} {cost:<10}")
    
    print("-" * 100)


def save_report_to_file(reports: list, filename: str):
    """将报告保存到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"空调使用详细记录报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*80}\n\n")
        
        grand_total_cost = Decimal("0.00")
        grand_total_energy = 0.0
        
        for report in reports:
            room_id = report["room_id"]
            f.write(f"\n{'='*80}\n")
            f.write(f"房间 {room_id} - 空调使用详细记录\n")
            f.write(f"{'='*80}\n")
            
            if report["total_records"] == 0:
                f.write("  暂无空调使用记录\n")
                continue
            
            grand_total_cost += report["total_cost"]
            grand_total_energy += report["total_energy"]
            
            # 汇总信息
            f.write(f"\n【汇总统计】\n")
            f.write(f"  总服务次数: {report['total_records']} 次\n")
            f.write(f"  总服务时长: {format_duration(report['total_duration'])}\n")
            f.write(f"  总能耗: {report['total_energy']:.4f} 度\n")
            f.write(f"  总费用: {report['total_cost']:.2f} 元\n")
            
            # 详单列表
            f.write(f"\n【详单记录】\n")
            f.write("-" * 100 + "\n")
            f.write(f"  {'序号':<6} {'开始时间':<12} {'结束时间':<12} {'时长':<10} {'起始温度':<10} {'结束温度':<10} {'目标温度':<10} {'风速':<8} {'费用':<10}\n")
            f.write("-" * 100 + "\n")
            
            for idx, record in enumerate(report["records"], 1):
                start_time = record["start_time"].strftime("%H:%M:%S") if record["start_time"] else "-"
                end_time = record["end_time"].strftime("%H:%M:%S") if record["end_time"] else "进行中"
                duration = format_duration(record["duration"]) if record["duration"] > 0 else "-"
                start_temp = f"{record['start_temp']:.1f}°C" if record["start_temp"] is not None else "-"
                end_temp = f"{record['end_temp']:.1f}°C" if record["end_temp"] is not None else "-"
                target_temp = f"{record['target_temp']:.1f}°C" if record["target_temp"] is not None else "-"
                fan_speed = record["fan_speed"] or "-"
                cost = f"{record['cost']:.2f}元" if record["cost"] else "-"
                
                fan_speed_cn = {"high": "高", "medium": "中", "low": "低"}.get(fan_speed, fan_speed)
                
                f.write(f"  {idx:<6} {start_time:<12} {end_time:<12} {duration:<10} {start_temp:<10} {end_temp:<10} {target_temp:<10} {fan_speed_cn:<8} {cost:<10}\n")
            
            f.write("-" * 100 + "\n")
        
        # 总计
        f.write(f"\n{'='*80}\n")
        f.write(f"【所有房间总计】\n")
        f.write(f"  总能耗: {grand_total_energy:.4f} 度\n")
        f.write(f"  总费用: {grand_total_cost:.2f} 元\n")
        f.write(f"{'='*80}\n")
    
    print(f"\n报告已保存到: {filename}")


def main():
    """主函数"""
    print("=" * 60)
    print("房间空调详细记录报告生成器")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取所有有记录的房间
    room_ids = ACDetailRecord.objects.values_list('room_id', flat=True).distinct()
    room_ids = sorted(set(room_ids))
    
    if not room_ids:
        # 如果没有记录，检查默认的5个房间
        room_ids = ["301", "302", "303", "304", "305"]
    
    print(f"\n检测到房间: {', '.join(room_ids)}")
    
    # 生成每个房间的报告
    reports = []
    for room_id in room_ids:
        report = generate_room_report(room_id)
        reports.append(report)
        print_room_report(report)
    
    # 打印总计
    print(f"\n{'='*80}")
    print("【所有房间总计】")
    print("=" * 80)
    
    grand_total_cost = sum(r["total_cost"] for r in reports)
    grand_total_energy = sum(r["total_energy"] for r in reports)
    grand_total_records = sum(r["total_records"] for r in reports)
    
    print(f"  总服务次数: {grand_total_records} 次")
    print(f"  总能耗: {grand_total_energy:.4f} 度")
    print(f"  总费用: {grand_total_cost:.2f} 元")
    
    # 保存到文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ac_report_{timestamp}.txt"
    save_report_to_file(reports, filename)
    
    print("\n报告生成完毕！")


if __name__ == "__main__":
    main()
