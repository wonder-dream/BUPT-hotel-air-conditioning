<template>
  <div class="monitor-page">
    <div class="page-header">
      <h1>空调使用状态监控（系统管理员）</h1>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 批量控制 -->
    <div class="bulk-controls">
      <div class="bulk-row">
        <span class="bulk-label">批量设置:</span>
        <el-select v-model="bulk.mode" placeholder="模式" clearable size="small" style="width: 100px">
          <el-option label="制冷" value="cooling" />
          <el-option label="制热" value="heating" />
        </el-select>
        <el-input-number v-model="bulk.targetTemp" :min="18" :max="30" size="small" placeholder="温度" style="width: 100px" />
        <el-select v-model="bulk.fanSpeed" placeholder="风速" clearable size="small" style="width: 100px">
          <el-option label="低风" value="low" />
          <el-option label="中风" value="medium" />
          <el-option label="高风" value="high" />
        </el-select>
        <el-button type="primary" size="small" @click="applyBulk">应用到全部</el-button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">总入住房间数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value running">{{ stats.running }}</div>
        <div class="stat-label">运行中</div>
      </div>
      <div class="stat-card">
        <div class="stat-value waiting">{{ stats.waiting }}</div>
        <div class="stat-label">等待中</div>
      </div>
      <div class="stat-card">
        <div class="stat-value standby">{{ stats.standby }}</div>
        <div class="stat-label">待机中</div>
      </div>
      <div class="stat-card">
        <div class="stat-value off">{{ stats.off }}</div>
        <div class="stat-label">已关闭</div>
      </div>
    </div>

    <!-- 房间选择器 -->
    <div class="room-selector">
      <span>查看房间:</span>
      <el-select v-model="selectedRoom" placeholder="选择房间" style="width: 150px">
        <el-option label="全部房间" value="all" />
        <el-option v-for="room in roomStates" :key="room.room_id" :label="room.room_id" :value="room.room_id" />
      </el-select>
    </div>

    <!-- 运行状态饼图（5个房间） -->
    <div class="pie-section">
      <h3>5房间空调运行状态</h3>
      <div class="pie-chart" :style="pieStyle"></div>
      <div class="pie-legend">
        <span class="legend-item"><span class="legend-color on"></span>开启 {{ pieData.opened }}</span>
        <span class="legend-item"><span class="legend-color off"></span>关闭 {{ pieData.closed }}</span>
      </div>
    </div>

    <!-- 房间状态卡片 -->
    <div class="rooms-container">
      <div 
        v-for="room in filteredRooms" 
        :key="room.room_id" 
        class="room-card"
        :class="{ collapsed: room._collapsed }"
      >
        <div class="card-header" @click="toggleCollapse(room)">
          <div class="header-left">
            <div class="status-badge" :class="getBadgeClass(room)"></div>
            <h3>房间 {{ room.room_id }}</h3>
            <span class="header-meta">
              {{ room.mode === 'cooling' ? '制冷' : '制热' }} · 
              费用: ¥{{ room.cost?.toFixed(2) || '0.00' }}
            </span>
          </div>
          <div class="header-right">
            <el-tag :type="getStatusType(room.status)" size="small">
              {{ getStatusText(room.status) }}
            </el-tag>
            <el-button size="small" text>
              {{ room._collapsed ? '展开' : '折叠' }}
            </el-button>
          </div>
        </div>
        
        <transition name="slide-fade">
          <div class="card-body" v-show="!room._collapsed">
            <div class="info-row">
              <span class="info-label">当前温度 / 目标温度:</span>
              <span class="info-value">{{ room.current_temp?.toFixed(1) || '--' }}°C</span>
              <span class="info-divider">/</span>
              <span class="info-value highlight">{{ room.target_temp }}°C</span>
            </div>
            <div class="info-row">
              <span class="info-label">当前风速:</span>
              <el-tag :type="getFanSpeedType(room.fan_speed)" size="small">
                {{ getFanSpeedText(room.fan_speed) }}
              </el-tag>
            </div>
            <div class="info-row">
              <span class="info-label">耗电量:</span>
              <span class="info-value">{{ room.energy_consumed?.toFixed(2) || '0.00' }} 度</span>
            </div>
            <div class="info-row">
              <span class="info-label">服务时长:</span>
              <span class="info-value">{{ formatDuration(room.service_duration) }}</span>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- 调度队列信息 -->
    <div class="queue-info">
      <div class="queue-card">
        <h3>服务队列 ({{ serviceQueue.length }}/3)</h3>
        <div class="queue-list">
          <div v-for="item in serviceQueue" :key="item.room_id" class="queue-item service">
            <span class="room">{{ item.room_id }}</span>
            <span class="speed">{{ getFanSpeedText(item.fan_speed) }}</span>
            <span class="duration">{{ formatDuration(item.service_duration) }}</span>
          </div>
          <div v-if="serviceQueue.length === 0" class="empty-hint">暂无</div>
        </div>
      </div>
      <div class="queue-card">
        <h3>等待队列 ({{ waitQueue.length }})</h3>
        <div class="queue-list">
          <div v-for="item in waitQueue" :key="item.room_id" class="queue-item waiting">
            <span class="room">{{ item.room_id }}</span>
            <span class="speed">{{ getFanSpeedText(item.fan_speed) }}</span>
            <span class="wait-time">等待: {{ item.remaining_wait?.toFixed(0) || '--' }}s</span>
          </div>
          <div v-if="waitQueue.length === 0" class="empty-hint">暂无</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const roomStates = ref([])
const selectedRoom = ref('all')
let refreshTimer = null
const defaultRooms = ['301','302','303','304','305']

// 批量控制
const bulk = reactive({
  mode: '',
  targetTemp: null,
  fanSpeed: ''
})

// 过滤后的房间
const filteredRooms = computed(() => {
  if (selectedRoom.value === 'all') {
    const preferred = roomStates.value.filter(r => defaultRooms.includes(String(r.room_id)))
    return preferred.length ? preferred : roomStates.value.slice(0, 5)
  }
  return roomStates.value.filter(r => r.room_id === selectedRoom.value)
})

// 饼图数据（5房间：开启 vs 关闭）
const fiveRooms = computed(() => {
  const preferred = roomStates.value.filter(r => defaultRooms.includes(String(r.room_id)))
  return preferred.length ? preferred : roomStates.value.slice(0, 5)
})
const pieData = computed(() => {
  const opened = fiveRooms.value.filter(r => r.status !== 'off').length
  const total = fiveRooms.value.length || 1
  return { opened, closed: total - opened, total }
})
const pieStyle = computed(() => {
  const percent = Math.round((pieData.value.opened / (pieData.value.total || 1)) * 100)
  return {
    background: `conic-gradient(#67c23a 0% ${percent}%, #c0c4cc ${percent}% 100%)`
  }
})

// 统计数据
const stats = computed(() => {
  const total = roomStates.value.length
  const running = roomStates.value.filter(r => r.status === 'on').length
  const waiting = roomStates.value.filter(r => r.status === 'waiting').length
  const standby = roomStates.value.filter(r => r.status === 'standby').length
  const off = roomStates.value.filter(r => r.status === 'off').length
  return { total, running, waiting, standby, off }
})

// 服务队列
const serviceQueue = computed(() => {
  return roomStates.value.filter(r => r.status === 'on')
})

// 等待队列
const waitQueue = computed(() => {
  return roomStates.value.filter(r => r.status === 'waiting')
})

// 刷新数据
const refreshData = async () => {
  try {
    const res = await api.getACMonitor()
    if (res.code === 200) {
      // 保持折叠状态
      const collapsedMap = {}
      roomStates.value.forEach(r => {
        collapsedMap[r.room_id] = r._collapsed
      })
      roomStates.value = res.data.map(r => ({
        ...r,
        _collapsed: collapsedMap[r.room_id] ?? false
      }))
    }
  } catch (error) {
    console.error('获取监控数据失败:', error)
  }
}

// 批量应用
const applyBulk = async () => {
  if (!bulk.mode && !bulk.targetTemp && !bulk.fanSpeed) {
    ElMessage.warning('请至少选择一项设置')
    return
  }
  
  try {
    for (const room of roomStates.value) {
      if (room.status !== 'off') {
        // 如果设置了模式或温度，发送调温请求
        if (bulk.mode || bulk.targetTemp) {
          await api.acControl({
            room_id: room.room_id,
            action: 'change_temp',
            mode: bulk.mode || room.mode,
            target_temp: bulk.targetTemp || room.target_temp
          })
        }
        // 如果设置了风速，发送调风速请求
        if (bulk.fanSpeed) {
          await api.acControl({
            room_id: room.room_id,
            action: 'change_speed',
            fan_speed: bulk.fanSpeed
          })
        }
      }
    }
    ElMessage.success('批量设置成功')
    refreshData()
  } catch (error) {
    ElMessage.error('批量设置失败')
    console.error(error)
  }
}

// 切换折叠状态
const toggleCollapse = (room) => {
  room._collapsed = !room._collapsed
}

// 状态徽标颜色（开启=绿，关闭=灰）
const getBadgeClass = (room) => {
  return room.status === 'off' ? 'off' : 'on'
}

// 状态类型
const getStatusType = (status) => {
  const map = {
    'on': 'success',
    'waiting': 'warning',
    'standby': 'info',
    'off': 'info'
  }
  return map[status] || 'info'
}

// 状态文本
const getStatusText = (status) => {
  const map = {
    'on': '运行中',
    'waiting': '等待中',
    'standby': '待机',
    'off': '关闭'
  }
  return map[status] || status
}

// 风速类型
const getFanSpeedType = (speed) => {
  const map = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger'
  }
  return map[speed] || ''
}

// 风速文本
const getFanSpeedText = (speed) => {
  const map = {
    'low': '低风',
    'medium': '中风',
    'high': '高风'
  }
  return map[speed] || speed
}

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}分${secs}秒`
}

onMounted(() => {
  refreshData()
  refreshTimer = setInterval(refreshData, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.monitor-page {
  padding: 20px 16px;
  background: #f5f7fa;
  min-height: 100vh;
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h1 {
  font-size: 20px;
  color: #333;
  font-weight: 500;
}

/* 批量控制 */
.bulk-controls {
  background: white;
  padding: 12px 14px;
  border-radius: 8px;
  margin-bottom: 14px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
}

.bulk-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.bulk-label {
  color: #666;
  font-weight: 500;
}

/* 房间选择器 */
.room-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  background: white;
  padding: 10px 14px;
  border-radius: 8px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
}

.pie-section {
  background: white;
  padding: 14px;
  border-radius: 8px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 14px;
}
.pie-section h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}
.pie-chart {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  margin: 6px auto;
  box-shadow: inset 0 0 8px rgba(0,0,0,0.05);
}
.pie-legend {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 6px;
  color: #666;
  font-size: 12px;
}
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}
.legend-color.on { background: #67c23a; }
.legend-color.off { background: #c0c4cc; }

.stats-overview {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 14px;
}

.stat-card {
  background: white;
  padding: 14px 12px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
}

.stat-value {
  font-size: 26px;
  font-weight: bold;
  color: #333;
}

.stat-value.running { color: #67c23a; }
.stat-value.waiting { color: #e6a23c; }
.stat-value.standby { color: #909399; }
.stat-value.off { color: #c0c4cc; }

.stat-label {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
}

/* 房间卡片 */
.rooms-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.room-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid #eef2f7;
}

.room-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  background: #fafbfc;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-badge {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.status-badge.on { background: #67c23a; }
.status-badge.waiting { background: #e6a23c; }
.status-badge.standby { background: #909399; }
.status-badge.off { background: #c0c4cc; }

.card-header h3 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.header-meta {
  color: #666;
  font-size: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-body {
  padding: 10px 12px;
  border-top: 1px solid #eee;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.info-label {
  width: 150px;
  color: #666;
  font-size: 12px;
}

.info-value {
  color: #333;
  font-weight: 500;
  font-size: 13px;
}

.info-value.highlight {
  color: #409eff;
}

.info-divider {
  color: #ccc;
}

/* 队列信息 */
.queue-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.queue-card {
  background: white;
  border-radius: 8px;
  padding: 14px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
}

.queue-card h3 {
  font-size: 14px;
  color: #333;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
}

.queue-item.service {
  background: #f0f9eb;
  color: #67c23a;
}

.queue-item.waiting {
  background: #fdf6ec;
  color: #e6a23c;
}

.queue-item .room {
  font-weight: bold;
}

.empty-hint {
  color: #999;
  text-align: center;
  padding: 16px;
}

/* 过渡动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.25s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .queue-info {
    grid-template-columns: 1fr;
  }
  
  .bulk-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
