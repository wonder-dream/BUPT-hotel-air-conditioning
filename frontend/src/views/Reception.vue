<template>
  <div class="reception-page">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <el-button 
        :type="activeTab === 'checkin' ? 'primary' : 'default'"
        size="large"
        @click="activeTab = 'checkin'"
      >
        入住办理
      </el-button>
      <el-button 
        :type="activeTab === 'checkout' ? 'primary' : 'default'"
        size="large"
        @click="activeTab = 'checkout'"
      >
        结账办理
      </el-button>
      <el-button 
        :type="activeTab === 'roomStatus' ? 'primary' : 'default'"
        size="large"
        @click="activeTab = 'roomStatus'; loadAllRooms()"
      >
        房间状态
      </el-button>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 入住办理 -->
      <div v-if="activeTab === 'checkin'" class="checkin-panel">
        <h2>客户信息</h2>
        <el-form :model="checkInForm" label-width="100px" class="checkin-form" @submit.prevent="handleCheckIn">
          <el-form-item label="姓名：">
            <el-input v-model="checkInForm.name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="手机号：">
            <el-input v-model="checkInForm.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="身份证号：">
            <el-input v-model="checkInForm.id_card" placeholder="请输入身份证号" />
          </el-form-item>
          <el-form-item label="房间号：">
            <el-select v-model="checkInForm.room_id" placeholder="选择房间">
              <el-option 
                v-for="room in availableRooms" 
                :key="room.room_id"
                :label="`${room.room_id} - ${room.room_type_display || room.room_type}`"
                :value="room.room_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleCheckIn">确认</el-button>
          </el-form-item>
        </el-form>

        <!-- 入住成功信息 -->
        <div v-if="checkInResult" class="result-panel">
          <h3>房间信息</h3>
          <div class="info-item">
            <span class="label">房型:</span>
            <span class="value highlight">{{ checkInResult.room_type }}</span>
          </div>
          <div class="info-item">
            <span class="label">房间数:</span>
            <span class="value highlight">1</span>
          </div>
          <div class="info-item">
            <span class="label">房号:</span>
            <span class="value highlight">{{ checkInResult.room_id }}</span>
          </div>
          <div class="info-item">
            <span class="label">入住时间:</span>
            <span class="value highlight">{{ checkInResult.check_in_time }}</span>
          </div>
          <div class="info-item">
            <span class="label">房费:</span>
            <span class="value highlight">¥{{ checkInResult.room_fee }}</span>
          </div>
        </div>
      </div>

      <!-- 结账办理 -->
      <div v-if="activeTab === 'checkout'" class="checkout-panel">
        <h2>结账办理</h2>
        <el-form :model="checkOutForm" label-width="100px" class="checkout-form" @submit.prevent="handleGetBill">
          <el-form-item label="房间号：">
            <el-input v-model="checkOutForm.room_id" placeholder="请输入房间号" @keyup.enter="handleGetBill" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleGetBill">确认</el-button>
          </el-form-item>
        </el-form>

        <!-- 结账详情 -->
        <div v-if="billDetail" class="result-panel bill-panel">
          <h3>结账详情</h3>
          <div class="info-item">
            <span class="label">房费:</span>
            <span class="value highlight">¥{{ billDetail.room_fee }}</span>
          </div>
          <div class="info-item">
            <span class="label">空调使用费:</span>
            <span class="value highlight">¥{{ billDetail.ac_fee }}</span>
          </div>
          <div class="info-item total">
            <span class="label">总计:</span>
            <span class="value highlight">¥{{ billDetail.total_fee }}</span>
          </div>
          <el-button type="primary" size="large" @click="handlePay" class="pay-btn">
            立即支付
          </el-button>
        </div>
      </div>

      <!-- 房间状态 -->
      <div v-if="activeTab === 'roomStatus'" class="room-status-panel">
        <h2>房间入住状态</h2>
        <el-button type="primary" @click="loadAllRooms" :icon="Refresh" class="refresh-btn">
          刷新
        </el-button>
        <div class="room-cards">
          <div 
            v-for="room in allRooms" 
            :key="room.room_id" 
            class="room-card"
            :class="{ 'occupied': room.is_occupied, 'available': !room.is_occupied }"
          >
            <div class="room-header">
              <span class="room-number">{{ room.room_id }}</span>
              <el-tag :type="room.is_occupied ? 'danger' : 'success'" size="small">
                {{ room.is_occupied ? '已入住' : '空闲' }}
              </el-tag>
            </div>
            <div class="room-type">{{ room.room_type_display || room.room_type }}</div>
            <template v-if="room.is_occupied && room.guest">
              <div class="guest-info">
                <div class="info-row">
                  <el-icon><User /></el-icon>
                  <span>{{ room.guest.name }}</span>
                </div>
                <div class="info-row">
                  <el-icon><Phone /></el-icon>
                  <span>{{ room.guest.phone }}</span>
                </div>
                <div class="info-row">
                  <el-icon><Postcard /></el-icon>
                  <span>{{ maskIdCard(room.guest.id_card) }}</span>
                </div>
                <div class="info-row">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatTime(room.guest.check_in_time) }}</span>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="empty-info">
                <span>暂无入住</span>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Phone, Postcard, Clock, Refresh } from '@element-plus/icons-vue'
import api from '../api'

const activeTab = ref('checkin')
const availableRooms = ref([])
const allRooms = ref([])

// 入住表单
const checkInForm = ref({
  name: '',
  phone: '',
  id_card: '',
  room_id: ''
})
const checkInResult = ref(null)

// 结账表单
const checkOutForm = ref({
  room_id: ''
})
const billDetail = ref(null)

// 获取可用房间
const loadAvailableRooms = async () => {
  try {
    const res = await api.getAvailableRooms()
    if (res.code === 200) {
      availableRooms.value = res.data
    }
  } catch (error) {
    console.error('获取房间列表失败:', error)
  }
}

// 获取所有房间状态
const loadAllRooms = async () => {
  try {
    const res = await api.getRooms()
    if (res.code === 200) {
      allRooms.value = res.data
    }
  } catch (error) {
    console.error('获取房间状态失败:', error)
  }
}

// 身份证号脱敏
const maskIdCard = (idCard) => {
  if (!idCard || idCard.length < 10) return idCard
  return idCard.substring(0, 4) + '**********' + idCard.substring(idCard.length - 4)
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 办理入住
const handleCheckIn = async () => {
  if (!checkInForm.value.name || !checkInForm.value.phone || 
      !checkInForm.value.id_card || !checkInForm.value.room_id) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  try {
    const res = await api.checkIn(checkInForm.value)
    if (res.code === 200) {
      checkInResult.value = res.data
      ElMessage.success('入住成功')
      loadAvailableRooms()
    } else {
      ElMessage.error(res.message || '入住失败')
    }
  } catch (error) {
    ElMessage.error('入住失败')
    console.error(error)
  }
}

// 获取账单
const handleGetBill = async () => {
  if (!checkOutForm.value.room_id) {
    ElMessage.warning('请输入房间号')
    return
  }
  
  try {
    const res = await api.getBillDetail(checkOutForm.value.room_id)
    if (res.code === 200) {
      billDetail.value = res.data
    } else {
      ElMessage.error(res.message || '获取账单失败')
    }
  } catch (error) {
    ElMessage.error('获取账单失败')
    console.error(error)
  }
}

// 支付
const handlePay = async () => {
  try {
    const res = await api.checkOut(checkOutForm.value.room_id)
    if (res.code === 200) {
      ElMessage.success('支付成功，已退房')
      billDetail.value = null
      checkOutForm.value.room_id = ''
      loadAvailableRooms()
    } else {
      ElMessage.error(res.message || '支付失败')
    }
  } catch (error) {
    ElMessage.error('支付失败')
    console.error(error)
  }
}

onMounted(() => {
  loadAvailableRooms()
})
</script>

<style scoped>
.reception-page {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 200px;
  background: white;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
}

.sidebar .el-button {
  height: 60px;
  font-size: 16px;
}

.main-content {
  flex: 1;
  padding: 40px;
  display: flex;
  gap: 40px;
}

.checkin-panel,
.checkout-panel {
  flex: 1;
}

h2 {
  color: #333;
  margin-bottom: 30px;
  font-weight: 500;
}

.checkin-form,
.checkout-form {
  max-width: 400px;
}

.el-input,
.el-select {
  width: 300px;
}

.result-panel {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-top: 30px;
}

.result-panel h3 {
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.info-item {
  display: flex;
  margin-bottom: 15px;
}

.info-item .label {
  width: 120px;
  color: #666;
}

.info-item .value {
  color: #333;
}

.info-item .value.highlight {
  color: #409eff;
  font-weight: 500;
}

.info-item.total {
  padding-top: 15px;
  border-top: 1px solid #eee;
  margin-top: 15px;
}

.info-item.total .value {
  font-size: 20px;
  color: #f56c6c;
}

.bill-panel {
  max-width: 350px;
}

.pay-btn {
  width: 100%;
  margin-top: 20px;
  height: 50px;
  font-size: 16px;
}

/* 房间状态面板样式 */
.room-status-panel {
  flex: 1;
}

.room-status-panel h2 {
  display: inline-block;
  margin-right: 20px;
}

.refresh-btn {
  margin-bottom: 20px;
}

.room-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.room-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.room-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.room-card.occupied {
  border-left: 4px solid #f56c6c;
}

.room-card.available {
  border-left: 4px solid #67c23a;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.room-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.room-type {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eee;
}

.guest-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.info-row .el-icon {
  color: #409eff;
}

.empty-info {
  text-align: center;
  padding: 20px 0;
  color: #999;
  font-size: 14px;
}
</style>
