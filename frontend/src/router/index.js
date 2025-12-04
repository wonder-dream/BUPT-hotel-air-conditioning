import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/reception'
  },
  // 每个房间独立的空调控制页面
  {
    path: '/room/301',
    name: 'Room301',
    component: () => import('../views/CustomerPanel.vue'),
    meta: { title: '301房间 - 空调控制', roomId: '301' }
  },
  {
    path: '/room/302',
    name: 'Room302',
    component: () => import('../views/CustomerPanel.vue'),
    meta: { title: '302房间 - 空调控制', roomId: '302' }
  },
  {
    path: '/room/303',
    name: 'Room303',
    component: () => import('../views/CustomerPanel.vue'),
    meta: { title: '303房间 - 空调控制', roomId: '303' }
  },
  {
    path: '/room/304',
    name: 'Room304',
    component: () => import('../views/CustomerPanel.vue'),
    meta: { title: '304房间 - 空调控制', roomId: '304' }
  },
  {
    path: '/room/305',
    name: 'Room305',
    component: () => import('../views/CustomerPanel.vue'),
    meta: { title: '305房间 - 空调控制', roomId: '305' }
  },
  {
    path: '/reception',
    name: 'Reception',
    component: () => import('../views/Reception.vue'),
    meta: { title: '前台服务' }
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('../views/Monitor.vue'),
    meta: { title: '空调监控' }
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('../views/Report.vue'),
    meta: { title: '统计报表' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '波普特酒店空调系统'
  next()
})

export default router
