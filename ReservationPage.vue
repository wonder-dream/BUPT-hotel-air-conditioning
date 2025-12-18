<template>
  <div class="reservation-page">
    <div class="reservation-card">
      <h1 class="title">客房在线预定</h1>
      <p class="subtitle">请选择房间并填写您的联系信息，前台将为您保留房间</p>

      <el-form :model="form" label-width="80px" class="form" @submit.prevent="handleReserve">
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="房间">
          <el-select
            v-model="form.room_id"
            placeholder="请选择房间"
            style="width: 260px"
          >
            <el-option
              v-for="room in availableRooms"
              :key="room.room_id"
              :label="`${room.room_id} - ${room.room_type_display || room.room_type}`"
              :value="room.room_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleReserve" :loading="submitting">
            提交预定
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="successInfo" class="success-info">
        <h3>预定成功</h3>
        <p>房间号：{{ successInfo.room_id }}（{{ successInfo.room_type }}）</p>
        <p>预定人：{{ successInfo.customer_name }} / {{ successInfo.phone }}</p>
        <p class="hint">请携带有效身份证件到前台办理入住，前台将按照您的姓名和手机号核对预定信息。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
const bgUrl = new URL('../../hotel.jpg', import.meta.url).href
const backgroundImageUrl = `url(${bgUrl})`

const form = ref({
  name: '',
  phone: '',
  room_id: ''
})

const availableRooms = ref([])
const submitting = ref(false)
const successInfo = ref(null)

const loadAvailableRooms = async () => {
  try {
    const res = await api.getAvailableRooms()
    if (res.code === 200) {
      availableRooms.value = res.data
    }
  } catch (e) {
    console.error('获取可预定房间失败:', e)
  }
}

const handleReserve = async () => {
  if (!form.value.name || !form.value.phone || !form.value.room_id) {
    ElMessage.warning('请完整填写预定信息')
    return
  }
  submitting.value = true
  try {
    const res = await api.reserve(form.value)
    if (res.code === 200) {
      ElMessage.success('预定成功')
      successInfo.value = res.data
      form.value = { name: '', phone: '', room_id: '' }
      loadAvailableRooms()
    } else {
      ElMessage.error(res.message || '预定失败')
    }
  } catch (e) {
    console.error('预定失败:', e)
    ElMessage.error('预定失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadAvailableRooms()
})
</script>

<style scoped>
.reservation-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: v-bind(backgroundImageUrl);
  background-size: cover;
  background-position: center;
  position: relative;
}

.reservation-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.35);
  backdrop-filter: blur(1.2px);
  pointer-events: none;
  z-index: 0;
}

.reservation-card {
  width: 480px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 32px 28px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
  position: relative;
  z-index: 1;
}

.title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  color: #303133;
}

.subtitle {
  margin-top: 8px;
  margin-bottom: 24px;
  text-align: center;
  color: #909399;
  font-size: 13px;
}

.form {
  margin-top: 8px;
}

.success-info {
  margin-top: 20px;
  padding: 14px 16px;
  border-radius: 10px;
  background: #fdf6ec;
  color: #e6a23c;
  font-size: 13px;
}

.success-info h3 {
  margin: 0 0 8px 0;
  font-size: 15px;
}

.success-info .hint {
  margin-top: 6px;
  color: #c45619;
}
</style>


