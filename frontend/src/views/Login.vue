<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand">
        <div class="brand-title">波普特廉价酒店</div>
        <div class="brand-sub">前台登录</div>
      </div>
      <el-form @submit.prevent="onLogin" class="form">
        <el-form-item>
          <el-input v-model="username" placeholder="账号" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="password" type="password" placeholder="密码" size="large" />
        </el-form-item>
        <el-form-item>
          <el-radio-group v-model="role">
            <el-radio label="frontdesk">前台</el-radio>
            <el-radio label="manager">经理</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-button type="primary" size="large" class="login-btn" @click="onLogin">登录</el-button>
      </el-form>
      <div class="hint">
        测试账号：bptljjd 密码：88888888<br>
        （适用于前台和经理登录）
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
const bgUrl = new URL('../../hotel.jpg', import.meta.url).href
const backgroundImageUrl = `url(${bgUrl})`

const router = useRouter()
const username = ref('')
const password = ref('')
const role = ref('frontdesk')  // 默认前台

const onLogin = () => {
  if (username.value === 'bptljjd' && password.value === '88888888') {
    if (role.value === 'frontdesk') {
      localStorage.setItem('frontdeskLogin', 'true')
      localStorage.setItem('frontdeskUser', username.value)
      ElMessage.success('前台登录成功')
      router.replace('/reception')
    } else if (role.value === 'manager') {
      localStorage.setItem('managerLogin', 'true')
      localStorage.setItem('managerUser', username.value)
      ElMessage.success('经理登录成功')
      router.replace('/manager-report')
    }
  } else {
    ElMessage.error('账号或密码错误')
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: v-bind(backgroundImageUrl);
  background-size: cover;
  background-position: center;
  position: relative;
}
.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.35);
  backdrop-filter: blur(1.2px);
  pointer-events: none;
  z-index: 0;
}
.login-card {
  width: 420px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  padding: 30px;
  position: relative;
  z-index: 1;
}
.brand {
  text-align: center;
  margin-bottom: 20px;
}
.brand-title {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 2px;
}
.brand-sub {
  font-size: 14px;
  color: #8a8f98;
  margin-top: 6px;
}
.form {
  margin-top: 10px;
}
.login-btn {
  width: 100%;
  margin-top: 10px;
}
.hint {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 12px;
}
</style>
