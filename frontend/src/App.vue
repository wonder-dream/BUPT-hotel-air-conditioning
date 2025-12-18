<template>
  <div id="app">
    <div class="app-bg"></div>
    <header class="hotel-header">
      <div class="brand">
        <span class="hotel-name">波普特廉价酒店</span>
      </div>
      <div class="header-right">
        <span class="tagline">舒适·实惠·贴心</span>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="hotel-footer">
      © 2025 波普特廉价酒店
    </footer>
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', sans-serif;
  background-color: #f5f7fa;
}

.hotel-header {
  position: sticky;
  top: 0;
  z-index: 100;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: linear-gradient(90deg, #3a7bd5, #00d2ff);
  color: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}
.brand .hotel-name {
  font-weight: 700;
  letter-spacing: 1px;
}
.header-right .tagline {
  opacity: 0.9;
}
.app-main {
  min-height: calc(100vh - 64px - 48px);
}
.hotel-footer {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a8f98;
}

.app-bg {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background-image: url('https://images.unsplash.com/photo-1551517343-4b1afacc983a?q=80&w=1920&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  filter: blur(2px);
  opacity: 0.35;
  z-index: -1;
}
</style>
