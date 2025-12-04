import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 房间相关
  getRooms() {
    return api.get('/rooms/')
  },
  getAvailableRooms() {
    return api.get('/rooms/available/')
  },
  
  // 入住/结账
  checkIn(data) {
    return api.post('/checkin/', data)
  },
  checkOut(roomId) {
    return api.post('/checkout/', { room_id: roomId })
  },
  getBillDetail(roomId) {
    return api.get(`/bill/${roomId}/`)
  },
  payBill(billId) {
    return api.post('/pay/', { bill_id: billId })
  },
  
  // 空调控制
  acControl(data) {
    return api.post('/ac/control/', data)
  },
  getACState(roomId) {
    return api.get(`/ac/state/${roomId}/`)
  },
  getACMonitor() {
    return api.get('/ac/monitor/')
  },
  
  // 订单和报表
  getOrders(status = null) {
    const params = status ? { status } : {}
    return api.get('/orders/', { params })
  },
  getReport(type = 'daily', date = null) {
    const params = { type }
    if (date) params.date = date
    return api.get('/report/', { params })
  }
}
