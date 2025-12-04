<template>
  <div class="report-page">
    <div class="page-header">
      <h1>统计报表</h1>
      <div class="header-actions">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="loadReport"
        />
        <el-button type="primary" @click="loadReport">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon income">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">¥{{ report.total_income?.toFixed(2) || '0.00' }}</div>
          <div class="stat-label">总收入</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon room">
          <el-icon><House /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">¥{{ report.total_room_income?.toFixed(2) || '0.00' }}</div>
          <div class="stat-label">房费收入</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon ac">
          <el-icon><WindPower /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">¥{{ report.total_ac_income?.toFixed(2) || '0.00' }}</div>
          <div class="stat-label">空调收入</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon checkin">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ report.total_checkins || 0 }}</div>
          <div class="stat-label">入住人数</div>
        </div>
      </div>
    </div>

    <!-- 订单列表 -->
    <div class="orders-section">
      <h2>订单记录</h2>
      <el-table :data="orders" style="width: 100%" stripe>
        <el-table-column prop="order_id" label="订单号" width="100" />
        <el-table-column prop="customer_name" label="客户姓名" width="120" />
        <el-table-column prop="room" label="房间号" width="100" />
        <el-table-column label="入住时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.check_in_time) }}
          </template>
        </el-table-column>
        <el-table-column label="退房时间" width="180">
          <template #default="{ row }">
            {{ row.check_out_time ? formatDateTime(row.check_out_time) : '--' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getOrderStatusType(row.status)">
              {{ getOrderStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="房费" width="120">
          <template #default="{ row }">
            ¥{{ row.room_fee }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Money, House, WindPower, User } from '@element-plus/icons-vue'
import api from '../api'

const selectedDate = ref(new Date().toISOString().split('T')[0])
const report = ref({})
const orders = ref([])

// 加载报表
const loadReport = async () => {
  try {
    const res = await api.getReport('daily', selectedDate.value)
    if (res.code === 200) {
      report.value = res.data
    }
  } catch (error) {
    console.error('获取报表失败:', error)
  }
}

// 加载订单
const loadOrders = async () => {
  try {
    const res = await api.getOrders()
    if (res.code === 200) {
      orders.value = res.data
    }
  } catch (error) {
    console.error('获取订单失败:', error)
  }
}

// 格式化日期时间
const formatDateTime = (datetime) => {
  if (!datetime) return '--'
  const d = new Date(datetime)
  return d.toLocaleString('zh-CN')
}

// 订单状态类型
const getOrderStatusType = (status) => {
  const map = {
    'active': 'success',
    'completed': 'info',
    'cancelled': 'danger'
  }
  return map[status] || 'info'
}

// 订单状态文本
const getOrderStatusText = (status) => {
  const map = {
    'active': '入住中',
    'completed': '已退房',
    'cancelled': '已取消'
  }
  return map[status] || status
}

onMounted(() => {
  loadReport()
  loadOrders()
})
</script>

<style scoped>
.report-page {
  padding: 30px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 24px;
  color: #333;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.income {
  background: #e6f7ff;
  color: #1890ff;
}

.stat-icon.room {
  background: #f6ffed;
  color: #52c41a;
}

.stat-icon.ac {
  background: #fff7e6;
  color: #fa8c16;
}

.stat-icon.checkin {
  background: #f9f0ff;
  color: #722ed1;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

.orders-section {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.orders-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}
</style>
