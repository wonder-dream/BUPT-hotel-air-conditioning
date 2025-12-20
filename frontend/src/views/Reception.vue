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
      <el-button 
        :type="activeTab === 'meal' ? 'primary' : 'default'"
        size="large"
        @click="activeTab = 'meal'"
      >
        酒店订餐
      </el-button>
      <el-button 
        type="danger"
        size="large"
        @click="handleLogout"
      >
        退出登录
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
            <el-select v-model="checkInForm.room_id" placeholder="选择或输入房间号" filterable allow-create>
              <el-option 
                v-for="room in roomsForCheckIn" 
                :key="room.room_id"
                :label="`${room.room_id} - ${room.room_type_display || room.room_type}${room.is_reserved ? '（已预定）' : ''}`"
                :value="room.room_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="押金：">
            <el-input v-model.number="checkInForm.deposit_amount" placeholder="请输入押金金额" />
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
            <span class="value highlight">¥{{ formatMoney(billDetail.room_fee) }}</span>
          </div>
          <div class="info-item">
            <span class="label">空调使用费:</span>
            <span class="value highlight">¥{{ formatMoney(billDetail.ac_fee) }}</span>
          </div>
          <div class="info-item">
            <span class="label">餐饮费:</span>
            <span class="value highlight">¥{{ formatMoney(billDetail.meal_fee || 0) }}</span>
          </div>
          <div class="info-item">
            <span class="label">押金抵扣:</span>
            <span class="value highlight">-¥{{ formatMoney(billDetail.deposit_amount || 0) }}</span>
          </div>
          <div class="info-item total">
            <span class="label">总计:</span>
            <span class="value highlight">¥{{ formatMoney(billDetail.total_fee) }}</span>
          </div>
          <el-button type="primary" size="large" @click="handlePay" class="pay-btn">
            立即支付
          </el-button>
          <el-button type="default" size="large" @click="handleShowDetails" class="print-btn">
            显示详单
          </el-button>
          <el-button type="default" size="large" @click="printBill" class="print-btn">
            打印账单
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
            :class="{
              'occupied': room.is_occupied,
              'reserved': room.is_reserved && !room.is_occupied,
              'available': !room.is_occupied && !room.is_reserved
            }"
          >
            <div class="room-header">
              <span class="room-number">{{ room.room_id }}</span>
              <el-tag
                v-if="room.is_occupied"
                type="danger"
                size="small"
              >
                已入住
              </el-tag>
              <el-tag
                v-else-if="room.is_reserved"
                type="warning"
                size="small"
              >
                已预定
              </el-tag>
              <el-tag
                v-else
                type="success"
                size="small"
              >
                空闲
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
              <div class="empty-info" v-if="room.is_reserved">
                <div class="info-row">
                  <el-icon><User /></el-icon>
                  <span>{{ room.reserved_customer_name || '—' }}</span>
                </div>
                <div class="info-row">
                  <el-icon><Phone /></el-icon>
                  <span>{{ room.reserved_phone || '—' }}</span>
                </div>
              </div>
              <div class="empty-info" v-else>
                <span>暂无入住</span>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- 酒店订餐 -->
      <div v-if="activeTab === 'meal'" class="meal-panel">
        <h2>酒店订餐</h2>
        <el-form :model="mealForm" label-width="100px" class="checkout-form" @submit.prevent="handleOrderMeal">
          <el-form-item label="房间号：">
            <el-input v-model="mealForm.room_id" placeholder="请输入在住房间号" />
          </el-form-item>
        </el-form>
        <div class="menu-list">
          <div class="menu-item" v-for="(m, idx) in menuItems" :key="idx">
            <div class="menu-name">{{ m.name }}</div>
            <div class="menu-price">¥{{ m.price }}</div>
            <el-input-number v-model="m.qty" :min="0" :max="20" />
          </div>
        </div>
        <div class="meal-summary">
          <span>合计：¥{{ formatMoney(mealTotal) }}</span>
          <el-button type="primary" :disabled="mealTotal<=0 || !mealForm.room_id" @click="handleOrderMeal">提交订单</el-button>
        </div>
        <div class="meal-orders" v-if="mealOrders.length">
          <h3>近期订餐</h3>
          <el-table :data="mealOrders" style="width: 100%" height="260">
            <el-table-column prop="created_at" label="时间" width="160" />
            <el-table-column label="明细">
              <template #default="{ row }">
                <span v-for="(it,i) in row.items" :key="i">{{ it.name }}×{{ it.qty }}&nbsp;</span>
              </template>
            </el-table-column>
            <el-table-column label="金额" width="120">
              <template #default="{ row }">¥{{ formatMoney(row.fee) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </div>

    </div>
    <el-dialog v-model="detailDialogVisible" title="空调运行详单" width="800px">
      <div ref="printArea" class="detail-summary">
        <div class="info-item">
          <span class="label">房间号:</span>
          <span class="value highlight">{{ acDetails?.room_id }}</span>
        </div>
        <div class="info-item">
          <span class="label">总服务次数:</span>
          <span class="value highlight">{{ acDetails?.summary?.total_records }}</span>
        </div>
        <div class="info-item">
          <span class="label">总时长:</span>
          <span class="value highlight">{{ Math.floor((acDetails?.summary?.total_duration_seconds || 0)/60) }} 分钟</span>
        </div>
      <div class="info-item">
        <span class="label">总能耗:</span>
        <span class="value highlight">{{ format2(acDetails?.summary?.total_energy) }} 度</span>
      </div>
      <div class="info-item">
        <span class="label">总费用:</span>
        <span class="value highlight">¥{{ formatMoney(acDetails?.summary?.total_cost) }}</span>
      </div>
      </div>
      <el-table :data="acDetails?.details || []" style="width: 100%" height="380">
        <el-table-column prop="seq" label="序号" width="70" />
        <el-table-column prop="start_time" label="开始时间" width="160" />
        <el-table-column label="结束时间" width="160">
          <template #default="{ row }">
            {{ row.end_time || new Date().toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="时长" width="100">
          <template #default="{ row }">
            {{ row.duration_seconds < 60 ? `${row.duration_seconds}秒` : `${(row.duration_seconds/60).toFixed(1)}分钟` }}
          </template>
        </el-table-column>
      <el-table-column label="温度" width="160">
        <template #default="{ row }">
          {{ format2(row.start_temp) }}°C → {{ row.end_temp == null ? '--' : format2(row.end_temp) }}°C / 目标 {{ format2(row.target_temp) }}°C
        </template>
      </el-table-column>
        <el-table-column label="模式/风速" width="140">
          <template #default="{ row }">
            {{ row.mode === 'cooling' ? '制冷' : '制热' }} / {{ row.fan_speed === 'low' ? '低' : (row.fan_speed === 'high' ? '高' : '中') }}
          </template>
        </el-table-column>
      <el-table-column prop="energy" label="耗电(度)" width="110" />
      <el-table-column label="费用" width="100">
        <template #default="{ row }">¥{{ formatMoney(row.cost) }}</template>
      </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="printDetails">打印</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Phone, Postcard, Clock, Refresh } from '@element-plus/icons-vue'
import api from '../api'
import { useRouter } from 'vue-router'

const activeTab = ref('checkin')
const availableRooms = ref([])
const roomsForCheckIn = ref([])
const allRooms = ref([])
const router = useRouter()

// 入住表单
const checkInForm = ref({
  name: '',
  phone: '',
  id_card: '',
  room_id: '',
  deposit_amount: 0
})
const checkInResult = ref(null)

// 结账表单
const checkOutForm = ref({
  room_id: ''
})
const billDetail = ref(null)
const detailDialogVisible = ref(false)
const acDetails = ref(null)
const printArea = ref(null)

// 订餐
const mealForm = ref({ room_id: '' })
const menuItems = ref([
  { name: '早餐套餐', price: 30, qty: 0 },
  { name: '扬州炒饭', price: 25, qty: 0 },
  { name: '牛肉面', price: 28, qty: 0 },
  { name: '可乐', price: 5, qty: 0 },
  { name: '橙汁', price: 8, qty: 0 }
])
const mealOrders = ref([])
const mealTotal = computed(() => menuItems.value.reduce((s, m) => s + m.price * (m.qty || 0), 0))

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

// 获取可办理入住的房间（空闲或已预定但未入住）
const loadRoomsForCheckIn = async () => {
  try {
    const res = await api.getRooms()
    if (res.code === 200) {
      roomsForCheckIn.value = (res.data || []).filter(r => !r.is_occupied)
    }
  } catch (error) {
    console.error('获取可办理入住房间失败:', error)
  }
}

// 获取所有房间状态
const loadAllRooms = async () => {
  try {
    const res = await api.getRooms()
    if (res.code === 200) {
      const blocked = ['101','102','103','104','105']
      allRooms.value = (res.data || []).filter(r => !blocked.includes(String(r.room_id)))
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
const format2 = (n) => Number(n || 0).toFixed(2)
const formatMoney = (n) => format2(n)

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
      loadRoomsForCheckIn()
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

const handleShowDetails = async () => {
  if (!checkOutForm.value.room_id) {
    ElMessage.warning('请输入房间号')
    return
  }
  try {
    const res = await api.getACDetails(checkOutForm.value.room_id)
    if (res.code === 200) {
      acDetails.value = res.data
      detailDialogVisible.value = true
    } else {
      ElMessage.error(res.message || '获取详单失败')
    }
  } catch (error) {
    ElMessage.error('获取详单失败')
    console.error(error)
  }
}

onMounted(() => {
  loadRoomsForCheckIn()
})

const handleLogout = () => {
  localStorage.removeItem('frontdeskLogin')
  localStorage.removeItem('frontdeskUser')
  ElMessage.success('已退出登录')
  router.replace('/login')
}

const printDetails = () => {
  try {
    const summaryHtml = printArea.value ? printArea.value.innerHTML : ''
    const rows = acDetails.value?.details || []
    const tableHtml = `
      <table>
        <thead>
          <tr>
            <th>序号</th>
            <th>开始时间</th>
            <th>结束时间</th>
            <th>时长</th>
            <th>温度</th>
            <th>模式/风速</th>
            <th>耗电(度)</th>
            <th>费用</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map(r => {
            const endTime = r.end_time || new Date().toLocaleString('zh-CN')
            const duration = r.duration_seconds < 60 ? `${r.duration_seconds}秒` : `${(r.duration_seconds/60).toFixed(1)}分钟`
            const tempText = `${Number(r.start_temp || 0).toFixed(2)}°C → ${r.end_temp == null ? '--' : Number(r.end_temp).toFixed(2)}°C / 目标 ${Number(r.target_temp || 0).toFixed(2)}°C`
            const modeText = `${r.mode === 'cooling' ? '制冷' : '制热'} / ${r.fan_speed === 'low' ? '低' : (r.fan_speed === 'high' ? '高' : '中')}`
            const energyText = Number(r.energy || 0).toFixed(2)
            const costText = Number(r.cost || 0).toFixed(2)
            return `
              <tr>
                <td>${r.seq ?? ''}</td>
                <td>${r.start_time ?? ''}</td>
                <td>${endTime}</td>
                <td>${duration}</td>
                <td>${tempText}</td>
                <td>${modeText}</td>
                <td>${energyText}</td>
                <td>¥${costText}</td>
              </tr>
            `
          }).join('')}
        </tbody>
      </table>
    `
    const w = window.open('', '_blank', 'width=900,height=600')
    if (!w) return
    w.document.write(`
      <html>
        <head>
          <title>空调运行详单</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .info-item { display: flex; margin-bottom: 10px; }
            .label { width: 100px; color: #666; }
            .value { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { border: 1px solid #ddd; padding: 8px; font-size: 12px; }
            th { background: #f5f7fa; }
            .summary { margin-bottom: 10px; }
          </style>
        </head>
        <body>
          <h2>空调运行详单</h2>
          <div class="summary">
            <div>调度次数: ${acDetails.value?.summary?.total_records ?? 0}</div>
          </div>
          ${summaryHtml}
          ${tableHtml}
        </body>
      </html>
    `)
    w.document.close()
    w.focus()
    w.print()
    w.close()
  } catch (e) {
    console.error('打印失败:', e)
  }
}

const printBill = async () => {
  if (!billDetail.value) {
    ElMessage.warning('请先获取账单')
    return
  }
  const roomId = checkOutForm.value.room_id
  let scheduleCount = acDetails.value?.room_id === roomId ? (acDetails.value?.summary?.total_records ?? 0) : null
  try {
    if (scheduleCount == null && roomId) {
      const res = await api.getACDetails(roomId)
      if (res.code === 200) {
        acDetails.value = res.data
        scheduleCount = acDetails.value?.summary?.total_records ?? 0
      }
    }
  } catch {}
  const w = window.open('', '_blank', 'width=900,height=600')
  if (!w) return
  const nowStr = new Date().toLocaleString('zh-CN')
  w.document.write(`
    <html>
      <head>
        <title>结账账单</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h2 { margin-bottom: 10px; }
          .meta { color: #666; margin-bottom: 15px; }
          .info-item { display: flex; margin-bottom: 10px; }
          .label { width: 120px; color: #666; }
          .value { color: #333; }
          .total { border-top: 1px solid #eee; padding-top: 12px; margin-top: 8px; font-size: 18px; color: #f56c6c; }
        </style>
      </head>
      <body>
        <h2>波普特廉价酒店 - 结账账单</h2>
        <div class="meta">房间号: ${roomId || '--'} · 出单时间: ${nowStr}</div>
        <div class="info-item">
          <span class="label">调度次数:</span>
          <span class="value">${scheduleCount ?? 0}</span>
        </div>
        <div class="info-item">
          <span class="label">房费:</span>
          <span class="value">¥${formatMoney(billDetail.value.room_fee)}</span>
        </div>
        <div class="info-item">
          <span class="label">空调使用费:</span>
          <span class="value">¥${formatMoney(billDetail.value.ac_fee)}</span>
        </div>
        <div class="info-item total">
          <span class="label">总计:</span>
          <span class="value">¥${formatMoney(billDetail.value.total_fee)}</span>
        </div>
      </body>
    </html>
  `)
  w.document.close()
  w.focus()
  w.print()
  w.close()
}

const handleOrderMeal = async () => {
  if (!mealForm.value.room_id) {
    ElMessage.warning('请输入房间号')
    return
  }
  const items = menuItems.value.filter(m => m.qty > 0).map(m => ({ name: m.name, qty: m.qty, price: m.price }))
  if (!items.length) {
    ElMessage.warning('请先选择菜品')
    return
  }
  try {
    const res = await api.orderMeal({ room_id: mealForm.value.room_id, items })
    if (res.code === 200) {
      ElMessage.success('下单成功')
      await loadMealOrders()
      menuItems.value.forEach(m => (m.qty = 0))
    } else {
      ElMessage.error(res.message || '下单失败')
    }
  } catch (e) {
    ElMessage.error('下单失败')
  }
}

const loadMealOrders = async () => {
  if (!mealForm.value.room_id) return
  try {
    const res = await api.getMealOrders(mealForm.value.room_id)
    if (res.code === 200) {
      mealOrders.value = res.data || []
    }
  } catch {}
}
</script>

<style scoped>
.reception-page {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
  position: relative;
}

.reception-page::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url('https://images.unsplash.com/photo-1469796466634-4f501ee0337f?q=80&w=1920&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  filter: blur(1.5px);
  opacity: 0.28;
  z-index: -1;
}

.sidebar {
  width: 220px;
  background: white;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}

.sidebar .el-button {
  height: 60px;
  font-size: 16px;
}

.main-content {
  flex: 1;
  padding: 30px 40px;
  display: flex;
  gap: 40px;
}

.meal-panel {
  flex: 1;
}
.menu-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin: 10px 0 16px;
}
.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 1px solid #eef2f7;
  padding: 12px;
  border-radius: 8px;
}
.menu-name { font-weight: 500; }
.menu-price { color: #666; }
.meal-summary { display: flex; align-items: center; gap: 16px; margin-top: 6px; }

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
  border: 1px solid #eef2f7;
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

.print-btn {
  width: 100%;
  margin-top: 10px;
  height: 50px;
  font-size: 16px;
}

.detail-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px 20px;
  margin-bottom: 10px;
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
  border: 1px solid #eef2f7;
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

.room-card.reserved {
  border-left: 4px solid #e6a23c;
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
