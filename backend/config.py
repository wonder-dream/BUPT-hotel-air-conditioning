# 系统配置文件

# 房间配置
TOTAL_ROOMS = 5  # 酒店总房间数 x
MAX_SERVICE_NUM = 3  # 同时服务上限 y
WAIT_TIME_SLICE = 120  # 等待时间片 s秒

# 温度配置
DEFAULT_TEMP = 25  # 缺省温度
COOLING_MIN_TEMP = 15  # 制冷最低温度
COOLING_MAX_TEMP = 30  # 制冷最高温度
HEATING_MIN_TEMP = 20  # 制热最低温度
HEATING_MAX_TEMP = 30  # 制热最高温度
TEMP_THRESHOLD = 1  # 温度偏离阈值，超过此值自动重启

# 初始室温（模拟环境温度）
INITIAL_ROOM_TEMP = 28  # 假设初始室温为28度

# 风速配置 (度/分钟)
FAN_SPEED_POWER = {
    "low": 1 / 3,  # 低风：1度/3分钟
    "medium": 0.5,  # 中风：1度/2分钟
    "high": 1.0,  # 高风：1度/1分钟
}

# 温度变化率 (度/分钟)
TEMP_CHANGE_RATE = {
    "low": 1 / 3,  # 低风：1度/3分钟
    "medium": 0.5,  # 中风：1度/2分钟
    "high": 1,  # 高风：1度/1分钟
}

# 关机回温速率
TEMP_RESTORE_RATE = 0.5  # 度/分钟

# 计费标准
PRICE_PER_DEGREE = 1  # 1元/度

# 风速优先级
FAN_SPEED_PRIORITY = {"low": 1, "medium": 2, "high": 3}

# 房间价格（元/天）
ROOM_PRICE = {
    "301": 100,   # 房间一 100元/天
    "302": 125,   # 房间二 125元/天
    "303": 150,   # 房间三 150元/天
    "304": 200,   # 房间四 200元/天
    "305": 100,   # 房间五 100元/天
}

# 时间缩放比例
TIME_SCALE = 6