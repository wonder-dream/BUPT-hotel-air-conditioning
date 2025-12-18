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
        <el-button type="primary" size="large" class="login-btn" @click="onLogin">登录</el-button>
      </el-form>
      <div class="hint">测试账号：bptljjd 密码：88888888</div>
    </div>
  </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { ElMessage } from 'element-plus'
  import { useRouter } from 'vue-router'
  
  const router = useRouter()
  const username = ref('')
  const password = ref('')
  
  const onLogin = () => {
    if (username.value === 'bptljjd' && password.value === '88888888') {
      localStorage.setItem('frontdeskLogin', 'true')
      localStorage.setItem('frontdeskUser', username.value)
      ElMessage.success('登录成功')
      router.replace('/reception')
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
    background: linear-gradient(135deg, #e6f0ff 0%, #f6fbff 100%);
  }
  .login-card {
    width: 420px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    padding: 30px;
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
