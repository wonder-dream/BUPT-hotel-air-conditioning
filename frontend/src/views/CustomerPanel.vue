<template>
  <div class="customer-panel">
    <!-- 顶部信息栏 -->
    <div class="header-bar">
      <div class="room-info">
        <span class="room-label">房间号: </span>
        <span class="room-number">{{ roomId }}</span>
        <span class="datetime">{{ currentDateTime }}</span>
      </div>
      <div class="mode-info">
        模式: <span class="mode-text">{{ modeText }}</span>
      </div>
    </div>

    <!-- 主控制区域 -->
    <div class="control-area">
      <!-- 空调状态卡片 -->
      <div class="control-card status-card">
        <div class="card-title">空调状态</div>
        <div class="status-content">
          <div class="status-row">
            <span class="status-text" :class="{ 'on': acState.is_on }">
              {{ acState.is_on ? '已开启' : '已关闭' }}
            </span>
            <el-button 
              :type="acState.is_on ? 'danger' : 'primary'" 
              size="small"
              @click="togglePower"
            >
              {{ acState.is_on ? '关闭' : '开启' }}
            </el-button>
          </div>
          <div class="mode-selector">
            <span>选择模式</span>
            <div class="mode-buttons">
              <el-button 
                :type="acState.mode === 'cooling' ? 'primary' : 'default'"
                @click="changeMode('cooling')"
                :disabled="!acState.is_on"
              >
                制冷
              </el-button>
              <el-button 
                :type="acState.mode === 'heating' ? 'primary' : 'default'"
                @click="changeMode('heating')"
                :disabled="!acState.is_on"
              >
                制热
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 温度设置卡片 -->
      <div class="control-card temp-card">
        <div class="card-title">设定温度</div>
        <div class="temp-content">
          <div class="temp-display">
            <el-button 
              circle 
              @click="decreaseTemp"
              :disabled="!acState.is_on"
            >
              <el-icon><Minus /></el-icon>
            </el-button>
            <span class="temp-value">{{ acState.target_temp }}<span class="temp-unit">°C</span></span>
            <el-button 
              circle 
              @click="increaseTemp"
              :disabled="!acState.is_on"
            >
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
          <el-slider 
            v-model="acState.target_temp" 
            :min="tempRange.min" 
            :max="tempRange.max"
            :disabled="!acState.is_on"
            @change="setTemperature"
          />
        </div>
      </div>

      <!-- 风速设置卡片 -->
      <div class="control-card speed-card">
        <div class="card-title">风速</div>
        <div class="speed-content">
          <div class="speed-buttons">
            <el-button 
              :type="acState.fan_speed === 'low' ? 'primary' : 'default'"
              @click="setFanSpeed('low')"
              :disabled="!acState.is_on"
            >
              低
            </el-button>
            <el-button 
              :type="acState.fan_speed === 'medium' ? 'primary' : 'default'"
              @click="setFanSpeed('medium')"
              :disabled="!acState.is_on"
            >
              中
            </el-button>
            <el-button 
              :type="acState.fan_speed === 'high' ? 'primary' : 'default'"
              @click="setFanSpeed('high')"
              :disabled="!acState.is_on"
            >
              高
            </el-button>
          </div>
          <div class="cost-display">
            <div class="cost-label">累计使用费用</div>
            <div class="cost-value">¥ {{ acState.cost?.toFixed(2) || '0.00' }}</div>
            <div class="cost-hint">(实时更新)</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部状态栏 -->
    <div class="status-bar">
      <div class="current-status">
        <span>当前: {{ modeText }} · {{ acState.current_temp?.toFixed(1) || '--' }}°C</span>
        <span class="separator">|</span>
        <span>风速: {{ fanSpeedText }}</span>
        <span v-if="acState.status === 'waiting'" class="waiting-hint">
          (等待服务中...)
        </span>
        <span v-if="acState.status === 'standby'" class="standby-hint">
          (已达目标温度，待机中)
        </span>
      </div>
      <div class="extra-buttons">
        <el-button size="small">童锁</el-button>
        <el-button size="small">菜单</el-button>
        <el-button size="small">定时</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { Minus, Plus } from '@element-plus/icons-vue'
import api from '../api'

// 从路由 meta 中获取房间号
const route = useRoute()
const roomId = computed(() => route.meta.roomId || '301')

const currentDateTime = ref('')
let timer = null
let refreshTimer = null

const acState = ref({
  is_on: false,
  status: 'off',
  mode: 'cooling',
  current_temp: 24,
  target_temp: 24,
  fan_speed: 'medium',
  cost: 0
})

// 计算属性
const modeText = computed(() => {
  return acState.value.mode === 'cooling' ? '制冷' : '制热'
})

const fanSpeedText = computed(() => {
  const map = { low: '低', medium: '中', high: '高' }
  return map[acState.value.fan_speed] || '中'
})

const tempRange = computed(() => {
  if (acState.value.mode === 'cooling') {
    return { min: 18, max: 25 }
  } else {
    return { min: 25, max: 30 }
  }
})

// 更新时间
const updateDateTime = () => {
  const now = new Date()
  currentDateTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载空调状态
const loadACState = async () => {
  try {
    const res = await api.getACState(roomId.value)
    if (res.code === 200) {
      acState.value = res.data
    }
  } catch (error) {
    console.error('获取空调状态失败:', error)
  }
}

// 开关机
const togglePower = async () => {
  try {
    const action = acState.value.is_on ? 'power_off' : 'power_on'
    const res = await api.acControl({
      room_id: roomId.value,
      action: action,
      target_temp: acState.value.target_temp,
      fan_speed: acState.value.fan_speed,
      mode: acState.value.mode
    })
    if (res.code === 200) {
      acState.value = res.data
    }
  } catch (error) {
    console.error('操作失败:', error)
  }
}

// 切换模式
const changeMode = async (mode) => {
  try {
    // 切换模式时调整温度到合适范围
    let newTemp = acState.value.target_temp
    if (mode === 'cooling' && newTemp > 25) {
      newTemp = 25
    } else if (mode === 'heating' && newTemp < 25) {
      newTemp = 25
    }
    
    const res = await api.acControl({
      room_id: roomId.value,
      action: 'change_temp',
      target_temp: newTemp,
      mode: mode
    })
    if (res.code === 200) {
      acState.value = res.data
    }
  } catch (error) {
    console.error('切换模式失败:', error)
  }
}

// 增加温度
const increaseTemp = () => {
  if (acState.value.target_temp < tempRange.value.max) {
    acState.value.target_temp += 1
    setTemperature()
  }
}

// 减少温度
const decreaseTemp = () => {
  if (acState.value.target_temp > tempRange.value.min) {
    acState.value.target_temp -= 1
    setTemperature()
  }
}

// 设置温度
const setTemperature = async () => {
  try {
    const res = await api.acControl({
      room_id: roomId.value,
      action: 'change_temp',
      target_temp: acState.value.target_temp,
      mode: acState.value.mode
    })
    if (res.code === 200) {
      acState.value = res.data
    }
  } catch (error) {
    console.error('设置温度失败:', error)
  }
}

// 设置风速
const setFanSpeed = async (speed) => {
  try {
    const res = await api.acControl({
      room_id: roomId.value,
      action: 'change_speed',
      fan_speed: speed
    })
    if (res.code === 200) {
      acState.value = res.data
    }
  } catch (error) {
    console.error('设置风速失败:', error)
  }
}

onMounted(() => {
  updateDateTime()
  timer = setInterval(updateDateTime, 1000)
  loadACState()
  // 每2秒刷新状态
  refreshTimer = setInterval(loadACState, 2000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.customer-panel {
  max-width: 900px;
  margin: 20px auto;
  padding: 20px;
  background: linear-gradient(135deg, #e8f4fc 0%, #f0f8ff 100%);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-radius: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.room-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.room-label {
  color: #666;
}

.room-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.datetime {
  color: #999;
  margin-left: 20px;
}

.mode-info {
  color: #666;
}

.mode-text {
  color: #409eff;
  font-weight: bold;
}

.control-area {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.control-card {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.card-title {
  font-size: 14px;
  color: #999;
  margin-bottom: 15px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-text {
  font-size: 20px;
  font-weight: bold;
  color: #999;
}

.status-text.on {
  color: #67c23a;
}

.mode-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mode-selector span {
  font-size: 12px;
  color: #999;
}

.mode-buttons {
  display: flex;
  gap: 10px;
}

.temp-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.temp-display {
  display: flex;
  align-items: center;
  gap: 20px;
}

.temp-value {
  font-size: 48px;
  font-weight: bold;
  color: #333;
}

.temp-unit {
  font-size: 24px;
  color: #999;
}

.speed-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.speed-buttons {
  display: flex;
  gap: 10px;
}

.cost-display {
  text-align: center;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.cost-label {
  font-size: 12px;
  color: #999;
}

.cost-value {
  font-size: 24px;
  font-weight: bold;
  color: #f56c6c;
  margin: 5px 0;
}

.cost-hint {
  font-size: 12px;
  color: #999;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.current-status {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #666;
}

.separator {
  color: #ddd;
}

.waiting-hint {
  color: #e6a23c;
  font-size: 12px;
}

.standby-hint {
  color: #67c23a;
  font-size: 12px;
}

.extra-buttons {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .control-area {
    grid-template-columns: 1fr;
  }
}
</style>
