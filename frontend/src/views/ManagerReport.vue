<template>
  <div class="report-container">
    <div class="header">
      <div class="header-left">
        <h2>经理详细报表</h2>
        <div class="filters">
          <label for="date">日期:</label>
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="date-picker"
          />
          <label for="range">报表范围:</label>
          <el-select v-model="range" placeholder="选择范围" class="range-select">
            <el-option label="日" value="daily" />
            <el-option label="周" value="weekly" />
            <el-option label="月" value="monthly" />
          </el-select>
        </div>
      </div>
      <div class="actions">
        <el-button type="primary" @click="exportReport">导出报表</el-button>
        <el-button type="danger" @click="logout">退出登录</el-button>
      </div>
    </div>
    <div class="summary">
      <el-card class="card">
        <div class="stat-value">¥{{ summary.total_room_income?.toFixed(2) || '0.00' }}</div>
        <div class="stat-label">总房费</div>
      </el-card>
      <el-card class="card">
        <div class="stat-value">¥{{ summary.total_ac_income?.toFixed(2) || '0.00' }}</div>
        <div class="stat-label">总空调费</div>
      </el-card>
      <el-card class="card">
        <div class="stat-value">¥{{ summary.total_meal_income?.toFixed(2) || '0.00' }}</div>
        <div class="stat-label">总餐饮费</div>
      </el-card>
      <el-card class="card">
        <div class="stat-value">¥{{ summary.total_deposit?.toFixed(2) || '0.00' }}</div>
        <div class="stat-label">总押金</div>
      </el-card>
      <el-card class="card">
        <div class="stat-value">¥{{ summary.net_income?.toFixed(2) || '0.00' }}</div>
        <div class="stat-label">净收入</div>
      </el-card>
    </div>
    <el-table :data="bills" style="width: 100%" stripe>
      <el-table-column prop="room_number" label="房间号" width="100" />
      <el-table-column prop="checkin_time" label="入住时间" width="180" />
      <el-table-column prop="checkout_time" label="离开时间" width="180" />
      <el-table-column prop="room_fee" label="房费" width="120">
        <template #default="{ row }">
          ¥{{ row.room_fee?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column prop="ac_fee" label="空调费" width="120">
        <template #default="{ row }">
          ¥{{ row.ac_fee?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column prop="meal_fee" label="餐饮费" width="120">
        <template #default="{ row }">
          ¥{{ row.meal_fee?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column prop="deposit_amount" label="押金" width="120">
        <template #default="{ row }">
          ¥{{ row.deposit_amount?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column prop="total_amount" label="总金额" width="120">
        <template #default="{ row }">
          ¥{{ row.total_amount?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const range = ref('daily')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const summary = ref({})
const bills = ref([])

const generateReport = async () => {
  try {
    const res = await api.getManagerReport(range.value, selectedDate.value)
    if (res.code === 200) {
      summary.value = res.data.summary
      bills.value = res.data.bills.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    } else {
      ElMessage.error(res.message || '获取报表失败')
    }
  } catch (error) {
    console.error('获取报表失败:', error)
    ElMessage.error('获取报表失败')
  }
}

const exportReport = () => {
  window.print()
}

const logout = () => {
  localStorage.removeItem('managerLogin')
  localStorage.removeItem('managerUser')
  router.push('/login')
}

onMounted(() => {
  generateReport()
})

watch([range, selectedDate], () => {
  generateReport()
})
</script>

<style scoped>
.report-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  gap: 60px; /* 加大header内部元素间距 */
}

.header-left h2 {
  margin-bottom: 10px;
  color: #333;
}

.filters {
  display: flex;
  align-items: center;
  gap: 40px; /* 加大filters内部元素间距 */
}

.date-picker {
  width: 180px; /* 日期框变长 */
}

.range-select {
  width: 100px; /* 范围框变小 */
}

.actions {
  display: flex;
  gap: 15px; /* 加大actions内部按钮间距 */
}

.summary {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .summary {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .actions {
    margin-top: 10px;
  }
}
</style>